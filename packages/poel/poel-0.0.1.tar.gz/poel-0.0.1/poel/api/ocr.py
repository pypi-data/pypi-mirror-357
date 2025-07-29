# -*- coding: UTF-8 -*-


import base64
import sys

import pymupdf

from poel.core.BaiduOCR import BaiduOCR
from poel.core.OCR import OCR
from poel.core.OfdOCR import OfdOCR


def get_ocr(configPath, id, key):
    ocr = OCR()
    ocr.set_config(configPath, id, key)
    return ocr


def do_api(OCR_NAME, img_path, img_url, configPath, id, key, pdf_path=None):
    """
    閫氳繃绫荤殑鏂规硶鍚嶏紝鐩存帴璋冪敤鏂规硶
    :return:
    """
    ocr = get_ocr(configPath, id, key)
    if pdf_path:
        # 鎵撳紑PDF鏂囦欢

        # 瀛樺偍鎵€鏈夐〉闈㈢殑璇嗗埆缁撴灉  1
        all_results = []

        # 閬嶅巻姣忎竴椤? 2
        pdf_page = 0
        # 鎵撳紑PDF鏂囦欢
        pdf = pymupdf.open(pdf_path)
        for page_num in range(pdf.page_count):
            temp_pdf = pymupdf.open(pdf_path)

            temp_pdf.select([page_num])

            base64_encoded_pdf = base64.b64encode(temp_pdf.write()).decode('utf-8')

            # 璇嗗埆褰撳墠椤? 3
            page_result = ocr.DoOCR(OCR_NAME, ImageBase64=base64_encoded_pdf, ImageUrl=img_url, IsPdf=True)

            # 灏嗗綋鍓嶉〉缁撴灉娣诲姞鍒版€荤粨鏋滀腑  4
            all_results.append(page_result)
            pdf_page += 1
            # 鍏抽棴PDF鏂囨。
            temp_pdf.close()
        pdf.close()
        # ocr_res = ocr.DoOCR(OCR_NAME, ImageBase64=base64_encoded_pdf, ImageUrl=img_url, IsPdf=True)
        # 濡傛灉鍙湁涓€椤碉紝鐩存帴杩斿洖缁撴灉 6
        if len(all_results) == 1:
            return all_results[0]
        # 鍚﹀垯杩斿洖鎵€鏈夐〉闈㈢殑缁撴灉鍒楄〃
        return all_results
        # pdf_data = file.read()
        # base64_encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
        # ocr_res = ocr.DoOCR(OCR_NAME, ImageBase64=base64_encoded_pdf, ImageUrl=img_url, IsPdf=True)
    elif img_url:
        ocr_res = ocr.DoOCR(OCR_NAME, ImageBase64=img_path, ImageUrl=img_url)
    else:
        ImageBase64 = img2base64(img_path)
        ocr_res = ocr.DoOCR(OCR_NAME, ImageBase64=ImageBase64, ImageUrl=img_url)
    return ocr_res


def AdvertiseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def ArithmeticOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def BankCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def BankSlipOCR(img_path=None, img_url=None, configPath=None, id=None, key=None, pdf_path=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key, pdf_path=pdf_path)


def BizLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def BusInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def BusinessCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def CarInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def ClassifyDetectOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def DriverLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def DutyPaidProofOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def EduPaperOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def EnglishOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def EnterpriseLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def EstateCertOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def FinanBillOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def FinanBillSliceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def FlightInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def FormulaOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def GeneralAccurateOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def GeneralBasicOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def GeneralEfficientOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def GeneralFastOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def GeneralHandwritingOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def HKIDCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def HmtResidentPermitOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def IDCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def ImageEnhancement(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def InstitutionOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def InsuranceBillOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def InvoiceGeneralOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def LicensePlateOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def MLIDCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def MLIDPassportOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def MainlandPermitOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def MixedInvoiceDetect(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def MixedInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def OrgCodeCertOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def PassportOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def PermitOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def PropOwnerCertOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def QrcodeOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def QueryBarCode(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def QuotaInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeContainerOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeHealthCodeOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeIndonesiaIDCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeMedicalInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeOnlineTaxiItineraryOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizePhilippinesDrivingLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizePhilippinesVoteIDOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeTableOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeThaiIDCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeTravelCardOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def ResidenceBookletOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RideHailingDriverLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RideHailingTransportLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def SealOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def ShipInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def SmartStructuralOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def TableOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def TaxiInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def TextDetect(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def TollInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def TrainTicketOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VatInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None, pdf_path=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key, pdf_path=pdf_path)


def VatInvoiceVerify(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VatInvoiceVerifyNew(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VatRollInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VehicleLicenseOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VehicleRegCertOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VerifyBasicBizLicense(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VerifyBizLicense(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VerifyEnterpriseFourFactors(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def VerifyOfdVatInvoiceOCR(ofd_file_path=None, ofd_file_url=None, id=None, key=None):
    ocr = OfdOCR()
    ocr.set_config(id, key)
    if ofd_file_path:
        with open(ofd_file_path, 'rb') as file:
            pdf_data = file.read()
            base64_encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
            ocr_res = ocr.DoOCR(OfdFileBase64=base64_encoded_pdf)
    elif ofd_file_url:
        ocr_res = ocr.DoOCR(OfdFileUrl=ofd_file_url)

    return ocr_res


def VinOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def WaybillOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def RecognizeGeneralInvoice(img_path=None, img_url=None, configPath=None, id=None, key=None):
    return do_api(OCR_NAME=str(sys._getframe().f_code.co_name),
                  img_path=img_path,
                  img_url=img_url,
                  configPath=configPath,
                  id=id, key=key)


def social_security_card(img_path, id, key):
    baidu_ocr = BaiduOCR(id, key)
    return baidu_ocr.social_security_card(img_path)


# def VatInvoiceOCR(img_path=None, img_url=None, configPath=None, id=None, key=None):
#     """
#     澧炲€肩◣鍙戠エ鐨勮瘑鍒?
#     :param img_path: 蹇呭～锛屽彂绁ㄧ殑鍥剧墖浣嶇疆
#     :param configPath: 閫夊～锛岄厤缃枃浠剁殑浣嶇疆锛屾湁榛樿鍊?
#     :return:
#     """
#
#     ocr = get_ocr(configPath)
#     if img_url:
#         ocr_res = ocr.VatInvoiceOCR(ImageBase64=img_path, ImageUrl=img_url)
#     else:
#         ImageBase64 = img2base64(img_path)
#         ocr_res = ocr.VatInvoiceOCR(ImageBase64=ImageBase64, ImageUrl=img_url)
#     return ocr_res


import json

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models

from poel.lib.CommonUtils import img2base64


def SmartStructuralOCRV2(id, key, img_path):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取

        cred = credential.Credential(id, key)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = ocr_client.OcrClient(cred, "", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.SmartStructuralOCRV2Request()
        params = {
            "ImageBase64": img2base64(img_path)
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SmartStructuralOCRV2Response的实例，与请求对象对应
        resp = client.SmartStructuralOCRV2(req)
        # 输出json格式的字符串回包
        return resp.to_json_string()

    except TencentCloudSDKException as err:
        return err


def SmartStructuralPro(id, key, img_path):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取

        cred = credential.Credential(id, key)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ocr.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = ocr_client.OcrClient(cred, "", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.SmartStructuralProRequest()
        params = {
            "ImageBase64": img2base64(img_path)
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个SmartStructuralProResponse的实例，与请求对象对应
        resp = client.SmartStructuralPro(req)
        # 输出json格式的字符串回包
        return resp.to_json_string()

    except TencentCloudSDKException as err:
        return err
