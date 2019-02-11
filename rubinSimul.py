from random import seed

import simul

if __name__ == '__main__':
    seed(32767)
    rec = simul.Record()

    # Szerverszoba, szerverek
    s01 = simul.Fogyaszto(1, "Szerver Vitani", 600, 30, simul.Ido.HAJNAL, simul.Ido.EJFEL)
    s02 = simul.Fogyaszto(2, "Szerver Micimacko", 500, 20, simul.Ido.HAJNAL, simul.Ido.EJFEL)
    s03 = simul.Fogyaszto(3, "Szerver Brian", 700, 40, simul.Ido.HAJNAL, simul.Ido.EJFEL)
    s04 = simul.Fogyaszto(4, "Szerver Csigabiga", 600, 60, simul.Ido.HAJNAL, simul.Ido.EJFEL)
    s05 = simul.Fogyaszto(5, "Szerver Csigabiga", 600, 60, simul.Ido.HAJNAL, simul.Ido.EJFEL)

    # Konyha
    k01 = simul.CiklikusFogyaszto(30, "Konyha Hútő", 100, 10, simul.Ido.HAJNAL, simul.Ido.EJFEL,
                                  7 * 60, 60,  # 7 percig hűt
                                  53 * 60, 60)  # 53 ig nem, és ez ismétlődik
    k02 = simul.CiklikusFogyaszto(31, "Konyha Mikro 1", 1100, 200,
                                  simul.Ido.getRandSec(11, 40, 0, 600), simul.Ido.getRandSec(13, 10, 0, 600),  # Ebéd
                                  3 * 60, 90,  # 3 percig működik
                                  1 * 60, 60)  # 1 percig nem, és ez ismétlődik
    k03 = simul.CiklikusFogyaszto(32, "Konyha Mikro 2", 900, 100,
                                  simul.Ido.getRandSec(11, 50, 0, 600), simul.Ido.getRandSec(13, 30, 0, 600),  # Ebéd
                                  4 * 60, 90,  # 4 percig működik
                                  2 * 60, 60)  # 2 percig nem, és ez ismétlődik
    k04 = simul.CiklikusFogyaszto(33, "Konyha Mikro 3", 1200, 100,
                                  simul.Ido.getRandSec(11, 30, 0, 600), simul.Ido.getRandSec(12, 50, 0, 600),  # Ebéd
                                  3 * 60, 90,  # 3 percig működik
                                  5 * 60, 60)  # 5 percig nem, és ez ismétlődik
    k05 = simul.SpotFogyaszto(34, "Konyha lámpa", 200, 10,
                              simul.Ido.getSec(8, 0, 0), simul.Ido.getSec(18, 59, 59),
                              5 * 60, 2 * 60, 30)

    # Adminisztrátor hölgyek
    a01 = simul.Fogyaszto(40, "Admin IldiPC", 400, 40,
                          simul.Ido.getRandSec(8, 30, 0, 1200), simul.Ido.getRandSec(16, 29, 59, 1200))
    a02 = simul.Fogyaszto(41, "Admin ZsaZsaPC", 350, 40,
                          simul.Ido.getRandSec(8, 20, 0, 600), simul.Ido.getRandSec(16, 19, 59, 600))
    a03 = simul.Fogyaszto(42, "Admin HajniPC", 450, 50,
                          simul.Ido.getRandSec(9, 00, 0, 1500), simul.Ido.getRandSec(16, 59, 59, 1500))
    a04 = simul.CiklikusFogyaszto(43, "Admin Radiátor", 3000, 300,
                                  simul.Ido.getRandSec(10, 0, 0, 600), simul.Ido.getRandSec(12, 5, 0, 600),  # Fáznak
                                  8 * 60, 90,  # 8 percig működik
                                  8 * 60, 60)  # 8 percig nem, és ez ismétlődik

    # Mérők
    m1 = simul.Mero(1, "Főmérő", [1, 2, 3, 4, 5, 30, 31, 32, 33, 34, 40, 41, 42, 43])
    m2 = simul.Mero(2, "Szerver", [1, 2, 3, 4, 5])
    m3 = simul.Mero(3, "Adminn", [40, 41, 42, 43])

    # Hálózat
    rubinHalo = simul.Halozat(rec)
    rubinHalo.fogyasztok += [s01, s02, s03, s04, s05,
                             k01, k02, k03, k04, k05,
                             a01, a02, a03, a04]
    rubinHalo.merok += [m1, m2, m3]

    # Szimuláció
    rubinHalo.iterateOverDay(15 * simul.Ido.PERC)
    rec.write("data/rubin-simul.json")

    # Data dictionaries
    fogyli = dict()
    for fogyaszto in rubinHalo.fogyasztok:
        fogyli[fogyaszto.id] = fogyaszto.nev
    print(fogyli)

    meali = dict()
    for mero in rubinHalo.merok:
        meali[mero.id] = mero.nev
    print(meali)
