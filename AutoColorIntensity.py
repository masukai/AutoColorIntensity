#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import glob
import cv2
import matplotlib.pyplot as plt
import numpy as np
import csv
import time

# _listはリスト
# np_はnp.arrayに格納されている


def main(scale, ext, name, HSV_u, HSV_l, cl, gauk, gaun, closing_on):  # メイン関数
    start_time = time.time()

    # 変数調整はここで行う
    PtoC = 1.0 / scale  # pixel to cm  ImageJ等で前もって計測
    # 校正の必要あり。複数枚で確認が要必要。
    extension = ext  # 拡張子は調節して使う
    size_ex = int(len(extension)) * -1
    # binaryとclosingの調節はMainPGArea内で直接行うこと

    # 以下メインの流れ
    folder_name = name
    path = "./" + folder_name
    os.chdir(path)
    name_list, area_list = procedure(
        PtoC, extension, size_ex, folder_name, HSV_u, HSV_l, cl, gauk, gaun, closing_on)
    os.chdir("../")
    savefile(folder_name, name_list, area_list)

    # 計測(実測)値と計算値の比較用 基本的にコメントアウト
    # verification(folder_name)

    if __name__ != 'AutoColorIntensity':
        print(">>> complete {0:.2f} sec <<<".format(time.time() - start_time))
        return
    else:
        return time.time() - start_time


def procedure(PtoC, extension, size_ex, folder_name, HSV_u, HSV_l, cl, gauk, gaun, closing_on):
    jpg_list = glob.glob("*{0}".format(extension))  # JPGの探索とループ
    name_list = []
    area_list = []
    for i in range(len(jpg_list)):
        my_file = jpg_list[i]
        name = my_file[:size_ex]
        name_list.append(name)
        if __name__ != 'AutoArea':
            print("{0}/{1}: {2}".format(i + 1, len(jpg_list), name))
        img = cv2.imread(my_file)
        obj = MainPGArea(name, img, folder_name, HSV_u,
                         HSV_l, cl, gauk, gaun, closing_on)
        area_list.append(round(obj.pixels * (PtoC ** 2), 2))  # 小数点以下2桁
    return name_list, area_list


def savefile(folder_name, name_list, area_list):
    savecsv_buffer = np.array([name_list, area_list])
    savecsv = savecsv_buffer[:, np.argsort(savecsv_buffer[0])].T
    with open("{0}_calculated_area.csv".format(folder_name), "w") as f:
        writer = csv.writer(f, lineterminator="\n")
        for i in range(len(name_list)):
            writer.writerow(savecsv[i])
    return


def verification(folder_name):
    print("Start Verification")
    np_mea = np.loadtxt('measured_area.csv', delimiter=',', usecols=(1))
    np_cal = np.loadtxt('{0}_calculated_area.csv'.format(
        folder_name), delimiter=',', usecols=(1))
    print("Measured: {0}".format(np_mea))
    print("Calculated: {0}".format(np_cal))

    # 可視化
    np_check = np.array([-10000, 10000])

    coef_1 = np.polyfit(np_mea, np_cal, 1)
    print("y = ax + b")
    print("a: {0}".format(coef_1[0]))
    print("b: {0}".format(coef_1[1]))
    y_pred_1 = coef_1[0] * np_check + coef_1[1]

    ax = plt.figure(num=0, dpi=360).gca()
    ax.set_title("Verification", fontsize=14)
    ax.scatter(np_mea, np_cal, s=2, color="red", label="Verification")
    ax.scatter(np.mean(np_mea), np.mean(np_cal), s=40,
               marker="*", color="purple", label="Mean Value")
    ax.plot(np_check, y_pred_1, linewidth=1, color="red",
            label="fitting: y={0:.2f}x+{1:.2f}".format(coef_1[0], coef_1[1]))  # 最小2乗法 1次式
    ax.plot(np_check, np_check, linewidth=1, color="black", label="y=x")
    plt.grid(which='major')
    plt.legend()
    ax.set_xlim([0, 3000])
    ax.set_ylim([0, 3000])
    ax.set_xlabel('Measured', fontsize=14)
    ax.set_ylabel('Calculated', fontsize=14)
    ax.set_aspect('equal', adjustable='box')
    plt.savefig("Verification.png", bbox_inches='tight', pad_inches=0.1)
    plt.pause(0.3)  # 計算速度を上げる場合はコメントアウト
    plt.clf()
    return


class MainPGArea:  # 色調に差があり、輪郭になる場合HSVに変換>>>2値化して判別
    def __init__(self, file_name, img, folder_name, HSV_u, HSV_l, cl, gauk, gaun, closing_on):
        self.file_name = file_name
        self.img = img
        self.folder_name = folder_name
        self.HSV_u = HSV_u
        self.HSV_l = HSV_l
        self.cl = cl
        self.gauk = gauk
        self.gaun = gaun
        self.closing_on = closing_on
        self.pixels = 0
        self.hsv_transration()
        self.gauss_transration()
        self.hsv_binary()
        if self.closing_on:
            self.closing()
        self.intensity()
        self.BGR()
        self.GRAY()
        self.save_image()
        self.calculation_area()

    def hsv_transration(self):  # 色調変換
        self.hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        return

    def gauss_transration(self):  # ガウス変換
        self.gauss = cv2.GaussianBlur(
            self.hsv, (self.gauk, self.gauk), self.gaun)  # フィルタの大きさ
        return

    def hsv_binary(self):  # HSV制限2値化
        lower = np.array(self.HSV_l)  # 下限 0 0 0
        upper = np.array(self.HSV_u)  # 上限 180 255 255
        self.bin = cv2.inRange(self.gauss, lower, upper)
        return

    def closing(self):  # 膨張収縮処理により穴埋め
        kernel = np.ones((self.cl, self.cl), np.uint8)
        self.cl = cv2.morphologyEx(self.bin, cv2.MORPH_CLOSE, kernel)
        return

    def intensity(self):
        if self.closing_on:
            filter = np.array([self.cl] * 3)
        else:
            filter = np.array([self.bin] * 3)
        filter = np.transpose(filter, (1, 2, 0))
        self.check = self.hsv * filter
        return

    def BGR(self):
        self.bgr = cv2.cvtColor(self.check, cv2.COLOR_HSV2RGB_FULL)
        # self.bgr = cv2.cvtColor(self.check, cv2.COLOR_HSV2BGR)
        return

    def GRAY(self):
        gamma22LUT = np.array([pow(x / 255.0, 2.2) for x in range(256)],
                              dtype='float32')
        img_bgrL = cv2.LUT(self.bgr, gamma22LUT)
        img_grayL = cv2.cvtColor(img_bgrL, cv2.COLOR_BGR2GRAY)
        self.gray = pow(img_grayL, 1.0 / 2.2) * 255
        data = np.ravel(self.gray)
        data_0 = data[data > 0]
        path = "../{0}_save_values".format(self.folder_name)
        os.makedirs(path, exist_ok=True)
        os.chdir(path)
        with open("{0}_pixels_value.csv".format(self.file_name), "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(["mean", np.mean(data_0)])
            writer.writerow(["values"])
            for i in range(len(data_0)):
                writer.writerow([data_0[i]])
        os.chdir("../{0}".format(self.folder_name))
        # print(data_0)

        hist, edges = np.histogram(data_0, bins=16, density=True)
        w = edges[1] - edges[0]
        hist = hist * w
        path = "../{0}_save_hist".format(self.folder_name)
        os.makedirs(path, exist_ok=True)
        os.chdir(path)
        plt.bar(edges[:-1], hist, w, color="gray", edgecolor="black")
        plt.plot([np.mean(data_0), np.mean(data_0)], [0, 1], color="red",
                 label="mean: {0:.2f}".format(np.mean(data_0)))
        plt.xlabel("Grayscale values")
        plt.ylabel("Probability of occurrence, bins=16")
        plt.ylim(0, 0.5)
        plt.legend()
        plt.savefig("hist_{0}.png".format(self.file_name), dpi=360, bbox_inches='tight', pad_inches=0.1)
        # plt.pause(0.3)  # 計算速度を上げる場合はコメントアウト
        plt.clf()
        os.chdir("../{0}".format(self.folder_name))
        return

    def save_image(self):  # 画像の保存
        path = "../{0}_save_image".format(self.folder_name)
        os.makedirs(path, exist_ok=True)
        os.chdir(path)
        # cv2.imwrite("{0}_hsv.jpg".format(self.file_name), self.hsv)
        # cv2.imwrite("{0}_gauss.jpg".format(self.file_name), self.gauss)
        # cv2.imwrite("{0}_bin.jpg".format(self.file_name), self.bin)
        if self.closing_on:
            cv2.imwrite("{0}_cl.jpg".format(self.file_name), self.cl)
        else:
            cv2.imwrite("{0}_bin.jpg".format(self.file_name), self.bin)
        # cv2.imwrite("{0}_check.jpg".format(self.file_name), self.check)
        cv2.imwrite("{0}_bgr.jpg".format(self.file_name), self.bgr)
        cv2.imwrite("{0}_gray.jpg".format(self.file_name), self.gray)
        os.chdir("../{0}".format(self.folder_name))
        return

    def calculation_area(self):  # 面積pixel分の計算
        if self.closing_on:
            self.pixels = cv2.countNonZero(self.cl)  # 計算する画像の名前に変更
        else:
            self.pixels = cv2.countNonZero(self.bin)
        return


if __name__ == '__main__':
    scale = 28.3889
    ext = ".jpg"
    name = "photo"
    HSV_u = [36, 255, 95]
    HSV_l = [3, 48, 0]
    cl = 19
    gauk = 15
    gaun = 3
    closing_on = True
    main(scale, ext, name, HSV_u, HSV_l, cl, gauk, gaun, closing_on)
