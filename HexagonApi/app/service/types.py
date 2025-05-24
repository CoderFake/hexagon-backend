from enum import IntEnum


class PrintType(IntEnum):
    A4_COLOR_SINGLE_SIDE = 1
    B4_COLOR_SINGLE_SIDE = 2
    A3_COLOR_SINGLE_SIDE = 3
    A4_BW_SINGLE_SIDE = 4
    A4_BW_DOUBLE_SIDE = 5
    B4_BW_SINGLE_SIDE = 6
    A3_BW_DOUBLE_SIDE = 7


class ProductType(IntEnum):
    CV = 1
    WORK_HISTORY = 2


class Prefectures(IntEnum):
    HOKKAIDO = 1  # Hokkaido
    AOMORI = 2  # Aomori Prefecture
    IWATE = 3  # Iwate Prefecture
    MIYAGI = 4  # Miyagi Prefecture
    AKITA = 5  # Akita Prefecture
    YAMAGATA = 6  # Yamagata Prefecture
    FUKUSHIMA = 7  # Fukushima Prefecture
    IBARAKI = 8  # Ibaraki Prefecture
    TOCHIGI = 9  # Tochigi Prefecture
    GUNMA = 10  # Gunma Prefecture
    SAITAMA = 11  # Saitama Prefecture
    CHIBA = 12  # Chiba Prefecture
    TOKYO = 13  # Tokyo Metropolis
    KANAGAWA = 14  # Kanagawa Prefecture
    NIIGATA = 15  # Niigata Prefecture
    TOYAMA = 16  # Toyama Prefecture
    ISHIKAWA = 17  # Ishikawa Prefecture
    FUKUI = 18  # Fukui Prefecture
    YAMANASHI = 19  # Yamanashi Prefecture
    NAGANO = 20  # Nagano Prefecture
    GIFU = 21  # Gifu Prefecture
    SHIZUOKA = 22  # Shizuoka Prefecture
    AICHI = 23  # Aichi Prefecture
    MIE = 24  # Mie Prefecture
    SHIGA = 25  # Shiga Prefecture
    KYOTO = 26  # Kyoto Prefecture
    OSAKA = 27  # Osaka Prefecture
    HYOGO = 28  # Hyogo Prefecture
    NARA = 29  # Nara Prefecture
    WAKAYAMA = 30  # Wakayama Prefecture
    TOTTORI = 31  # Tottori Prefecture
    SHIMANE = 32  # Shimane Prefecture
    OKAYAMA = 33  # Okayama Prefecture
    HIROSHIMA = 34  # Hiroshima Prefecture
    YAMAGUCHI = 35  # Yamaguchi Prefecture
    TOKUSHIMA = 36  # Tokushima Prefecture
    KAGAWA = 37  # Kagawa Prefecture
    EHIME = 38  # Ehime Prefecture
    KOCHI = 39  # Kochi Prefecture
    FUKUOKA = 40  # Fukuoka Prefecture
    SAGA = 41  # Saga Prefecture
    NAGASAKI = 42  # Nagasaki Prefecture
    KUMAMOTO = 43  # Kumamoto Prefecture
    OITA = 44  # Oita Prefecture
    MIYAZAKI = 45  # Miyazaki Prefecture
    KAGOSHIMA = 46  # Kagoshima Prefecture
    OKINAWA = 47  # Okinawa Prefecture

    @classmethod
    def list(cls) -> list:
        return [{"id": p.value, "name": p.name} for p in cls]


class EmploymentTypes(IntEnum):
    FULL_TIME = 1  # Full-time employee
    CONTRACT = 2  # Contract employee
    PART_TIME = 3  # Part-time worker
    TEMPORARY = 4  # Temporary worker
    COMMISSION = 5  # Commission-based worker
    DISPATCH = 6  # Dispatch worker

    @classmethod
    def list(cls) -> list:
        return [{"id": e.value, "name": e.name} for e in cls]
