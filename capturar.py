import os
import re
import sys
import time
import json
import zipfile
import subprocess
import requests
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = "VictorP-Sec/camarasview2"
PROXY = "https://camarasview2.vercel.app/api/proxy"
MINUTOS_RETENER = 10080  # 7 dias

def gh(*args):
    r = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  gh error: {r.stderr.strip()}")
    return r.stdout.strip()

def main():
    CAMERAS = [
        (2, "C BELLEA DEL FOC", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C52M3.jpg?itok=ktqVY-XN"),
        (3, "C ORION", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C11M5.jpg?itok=0cgKRmwy"),
        (4, "CARDENAL FRANCISCO ALVAREZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C29M6.jpg?itok=FOrqa30Q"),
        (5, "DR JIMENEZ DIAZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C29M4.jpg?itok=Y8CQk6-U"),
        (6, "AVDA NOVELDA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C39F3.jpg?itok=bSrCE-tR"),
        (7, "PLAZA DEL MILENIO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C52M2.jpg?itok=GmfyLoGq"),
        (8, "C MEXICO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C19M4.jpg?itok=BvOYg6rO"),
        (9, "C PINTOR XAVIER SOLER", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C52M4.jpg?itok=qDfjrER2"),
        (10, "DR JIMENEZ DIAZ 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C29M3.jpg?itok=PnF9s481"),
        (11, "C DR RICO CAMPO DE MIRRA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C54M1.jpg?itok=UxQdl1KP"),
        (12, "AV ORIHUELA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C11M4.jpg?itok=r3cXc6qD"),
        (13, "A 31", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C19M2.jpg?itok=oBHrBvX5"),
        (14, "C MEXICO 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C22M4.jpg?itok=bu2at0Wb"),
        (15, "AVDA BLASCO IBANEZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C24M3.jpg?itok=nW0YZ5il"),
        (16, "DR JIMENEZ DIAZ 3", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C29M1.jpg?itok=lrmp0MYg"),
        (17, "ALCALDE LORENZO CARBONELL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C22M2.jpg?itok=mNmDMC7L"),
        (18, "AL CARBONELL CAT SOLER", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C22M3.jpg?itok=3xHATAXl"),
        (19, "GRAN VIA PUENTE ROJO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C24F2.jpg?itok=CQhlqGoZ"),
        (20, "BULEVAR DE TEULADA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C13M5.jpg?itok=hk1gjG33"),
        (21, "GRAN VIA C ISLA DE CORFU", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C29M2.jpg?itok=rNXu0qpY"),
        (22, "MARCELINO CHAMPAGNAT", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C29M5.jpg?itok=hMd73UGO"),
        (23, "AVDA SANTA POLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C13M4.jpg?itok=tsmYWBkw"),
        (24, "GRAN VIA AV ORIHUELA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C11M1.jpg?itok=NHSoIkHa"),
        (25, "AVDA DR JIMENEZ DIAZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C13M2.jpg?itok=4hNnhXYj"),
        (26, "C TEULADA EF RICO PEREZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C13M3.jpg?itok=e6w7cyiN"),
        (27, "AVDA DR JIMENEZ DIAZ 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C11M3.jpg?itok=zVcVbGOL"),
        (28, "GRAN VIA AV ORIHUELA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C11M2.jpg?itok=M8PpBN9D"),
        (29, "GRAN VIA BABEL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C19F3.jpg?itok=GspY1yr6"),
        (30, "GRAN VIA ALTOZANO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C08F2.jpg?itok=B9dYkwP8"),
        (31, "C DEL MAESTRO ALONSO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C08F6.jpg?itok=dHunh88y"),
        (32, "C DEL MAESTRO ALONSO 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C08F3.jpg?itok=EVIbz5Sa"),
        (33, "GRAN VIA MAESTRO ALONSO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C08F5.jpg?itok=tkKXCaB5"),
        (34, "GRAN VIA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C08F4.jpg?itok=5gdVK_ZH"),
        (35, "GRAN VIA AVDA NOVELDA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C39F5.jpg?itok=xR3aVmc9"),
        (36, "GRAN VIA AV BUENOS AIRES", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C39F4.jpg?itok=__O20mKa"),
        (37, "GRAN VIA AVDA COLOMBIA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C39F2.jpg?itok=VuSTAP8-"),
        (38, "SALAMANCA ESTACION", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C35F4.jpg?itok=MpgZFZVp"),
        (39, "AVDA AGUILERA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C01F4.jpg?itok=5bER9ZLG"),
        (40, "OSCAR ESPLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C02F5.jpg?itok=ic65iwAY"),
        (41, "AVDA JIJONA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C09M4.jpg?itok=BkuxrdGk"),
        (42, "C SAN FERNANDO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C16F3.jpg?itok=bBIv8nxx"),
        (43, "OSCAR ESPLA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C01M5.jpg?itok=N2QI7Hpq"),
        (44, "C VAZQUEZ DE MELLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C55M1.jpg?itok=lgpQYfEj"),
        (45, "AVDA DE LA ESTACION", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C10F2.jpg?itok=DrT9DIfQ"),
        (46, "SALAMANCA ESTACION 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C35F2.jpg?itok=SclSf87b"),
        (47, "L CASANOVA OSCAR ESPLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C02F3.jpg?itok=Z7CiHG1T"),
        (48, "E SEMPERE OSCAR ESPLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C02F2.jpg?itok=MWD4LuJz"),
        (49, "CAT SOLER OSCAR ESPLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C02F4.jpg?itok=8eNFAGNc"),
        (50, "OSCAR ESPLA 3", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C01F3.jpg?itok=4SKlaoaT"),
        (51, "OSCAR ESPLA CAT SOLER", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C02F6.jpg?itok=xuTcIBfe"),
        (52, "RAMBLA MENDEZ NUNEZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C16F2.jpg?itok=VdNERR6t"),
        (53, "BP GALDOS GRAL MARVA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C36F4.jpg?itok=5H7SXW0F"),
        (54, "AVDA DR GADEA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C17F2.jpg?itok=FOPbckH4"),
        (55, "AVDA SALAMANCA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C12F2.jpg?itok=UX31HMxD"),
        (56, "AVDA NOVELDA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C07M1.jpg?itok=rU946dn_"),
        (57, "C PINTOR MURILLO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C09F2.jpg?itok=CYXu76Ex"),
        (58, "C REYES CATOLICOS", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C17F3.jpg?itok=SQcRlgBo"),
        (59, "BP GALDOS GRAL MARVA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C36F3.jpg?itok=xw80e0lo"),
        (60, "BP GALDOS PZA ESPANA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C36F2.jpg?itok=UClZaiKh"),
        (61, "C CALDERON DE LA BARCA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C15F3.jpg?itok=F8nuVFKx"),
        (62, "CONDE LUMIARES AV ALCOY", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C07F2.jpg?itok=WU4T8amJ"),
        (63, "C BENITO PEREZ GALDOS", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C12F3.jpg?itok=EG41BYp0"),
        (64, "BP GALDOS SALAMANCA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C36F1.jpg?itok=rHjJLmav"),
        (65, "AVDA ALFONSO X EL SABIO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C15F2.jpg?itok=dMvADY21"),
        (66, "RAMBLA MENDEZ NUNEZ 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C15F5.jpg?itok=qL4AM8tw"),
        (67, "A EL SABIO SAN VICENTE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C15F4.jpg?itok=ezPCaGrh"),
        (68, "AVDA MAISONNAVE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C01F2.jpg?itok=DEuQ1vIh"),
        (69, "AVDA DE ALCOY", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C09M3.jpg?itok=ENwJ4U2h"),
        (70, "AVDA RAMOS CARRATALA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C51M2.jpg?itok=VbamDPG2"),
        (71, "C MONTESINOS PL CASTALLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C51M3.jpg?itok=ds3Rhwmi"),
        (72, "AVDA BULEVAR DE TEULADA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C37F6.jpg?itok=Mm4gjdt0"),
        (73, "AV UNIVERSIDAD FORTUNY", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C27M5.jpg?itok=wIG1a07O"),
        (74, "AVDA GASTON CASTELLO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C32M5.jpg?itok=t8hr4Q3u"),
        (75, "AVDA NOVELDA 3", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C25M4.jpg?itok=vPOv8212"),
        (76, "C DEL CUARZO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C33M1.jpg?itok=ByfluLv0"),
        (77, "AVDA JAIME I", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C25M2.jpg?itok=njNRZPS9"),
        (78, "C FORTUNY", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C27M2.jpg?itok=IrurkCg7"),
        (79, "C JOSE LUIS BARCELO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C32M3.jpg?itok=okWXWcHg"),
        (80, "AVDA UNICEF", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C32M6.jpg?itok=fF1_a-Fb"),
        (81, "AVDA NOVELDA RABASA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C34F4.jpg?itok=1kUMND07"),
        (82, "AVDA BARONIA DE POLOP", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C33M4.jpg?itok=EXtTx1mN"),
        (83, "C FORTUNY 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C34F5.jpg?itok=s6Fla1zP"),
        (84, "AVDA UNIVERSIDAD", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C27M4.jpg?itok=NDanDYu7"),
        (85, "C PINTOR GASTON CASTELLO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C33M3.jpg?itok=rADvCIES"),
        (86, "C POETA PEDRO SALINAS", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C32M2.jpg?itok=1TkNygEg"),
        (87, "AVDA TEULADA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C37F2.jpg?itok=1QJObaEo"),
        (88, "C DEL PADRE ARRUPE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C06M5.jpg?itok=pZZ8Du6h"),
        (89, "VIA PARQUE JAIME I", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C37F3.jpg?itok=_PnWFp8X"),
        (90, "AVDA BARONIA DE POLOP RABASA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C34F3.jpg?itok=GYZMaap9"),
        (91, "AVDA DENIA JUAN XXIII", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C06M2.jpg?itok=sxOLYKQn"),
        (92, "VILLAFRANQUEZA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C33M2.jpg?itok=rtOwODFs"),
        (93, "C MAESTRO ALONSO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C32M4.jpg?itok=4Hn3wIOp"),
        (94, "AV NOVELDA AV UNICEF", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C25M3.jpg?itok=yptLjCHS"),
        (95, "AVDA UNICEF RABASA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C25M5.jpg?itok=Sv1ZBOqY"),
        (96, "AVDA JAIME I 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C37F5.jpg?itok=CuBgLp89"),
        (97, "AV NOVELDA SAN VICENTE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C34F2.jpg?itok=jZ1qau6n"),
        (98, "JAIME I JUDOKA JA VALVERDE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C43F4.jpg?itok=JScG-CDL"),
        (99, "JAIME I FTAS TRADICIONALES", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C43F3.jpg?itok=PQQ-1ki5"),
        (100, "AVD JAIME I TEULADA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C43F2.jpg?itok=e6iCNADI"),
        (101, "FIESTAS P Y TRADICIONALES", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C41F3.jpg?itok=IWs33oCB"),
        (102, "C ISLA DE CORFU", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C41F4.jpg?itok=GzmvHNvC"),
        (103, "CAMARA C21F4", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C21F4.jpg?itok=78XDZAv1"),
        (104, "CAMARA C21F2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C21F2.jpg?itok=ZJ3uqx7d"),
        (105, "C RIO MUNI", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C21F5.jpg?itok=gr2_Ghkb"),
        (106, "N 330", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C21F3.jpg?itok=fznqM6SA"),
        (107, "DPTA ISABEL FERNANDEZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C41F5.jpg?itok=B3c-sw6U"),
        (108, "FIESTAS P Y TRADICIONALES 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C41F2.jpg?itok=NBgsgESu"),
        (109, "AVDA UNIVERSIDAD 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C37F4.jpg?itok=5hfmDvX9"),
        (110, "AV MARTIRES DE LA LIBERTAD", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C03M2.jpg?itok=K8SAt93P"),
        (111, "SALIDA PUERTO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C03M4.jpg?itok=oS2tpsEr"),
        (112, "AV JUAN BAUTISTA LAFORA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C03M3.jpg?itok=zUlMYPpA"),
        (113, "AVDA DE DENIA VISTAHERMOSA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C04F2.jpg?itok=LnWIaOqd"),
        (114, "AV RAMOS CARRATALA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C04F3.jpg?itok=kfZg2JBp"),
        (115, "AVDA ALBUFERETA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C56F1.jpg?itok=Onw-QxIq"),
        (116, "C DEP ALEJANDRA QUEREDA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C04F4.jpg?itok=cntVZ8Bz"),
        (117, "AVDA DENIA ACCESO A70", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C49M3.jpg?itok=JMBk5Gjl"),
        (118, "AVDA DE DENIA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C04F5.jpg?itok=PcYuQWfJ"),
        (119, "AVDA DENIA ACCESO A70 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C48M2.jpg?itok=YTdkNCGO"),
        (120, "AVDA DE DENIA SANTA FAZ", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C48M1.jpg?itok=wK6rhew2"),
        (121, "AVDA DENIA JUAN XXIII 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C14M3.jpg?itok=A_X3fRcT"),
        (122, "AVDA DENIA 3", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C06M4.jpg?itok=JG12rolu"),
        (123, "AVDA PADRE ESPLA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C06M3.jpg?itok=G2KMEudZ"),
        (124, "AVDA PINTOR XAVIER SOLER", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C14M2.jpg?itok=ZR5d3AgV"),
        (125, "AVDA DENIA 4", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C14M4.jpg?itok=vVPQ5iM8"),
        (126, "AVDA DENIA BON REPOS", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C30M4.jpg?itok=owqHBUSg"),
        (127, "AV DENIA TORRES DE LA HUERTA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C49M2.jpg?itok=x3Bm8RRQ"),
        (128, "AVDA DE ELCHE FEDERICO MAYO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C50M1.jpg?itok=6suge2Ah"),
        (129, "AVDA ELCHE N332", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C18M3.jpg?itok=XR4KHo21"),
        (130, "C MEXICO BABEL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C18M4.jpg?itok=TV_pZJ3-"),
        (131, "AVDA ELCHE BABEL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C18M2.jpg?itok=LzbrlAfs"),
        (132, "AVDA ELCHE N332 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C40F3.jpg?itok=fbOmRP-N"),
        (133, "AV ELCHE JC COMBALDIEU", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C40F4.jpg?itok=X9JSZh-n"),
        (134, "AVDA ELCHE 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C31F2.jpg?itok=z7COG0ET"),
        (135, "CTRA DEL SALADAR", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C28F3.jpg?itok=FetFQ1oc"),
        (136, "CASA DEL MEDITERRANEO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C31F3.jpg?itok=HSDqzrqH"),
        (137, "N 332", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C28F2.jpg?itok=MyGA31yz"),
        (138, "AVDA LORING", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C31F4.jpg?itok=uwAoD7fo"),
        (139, "AVDA ELCHE 3", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C40F2.jpg?itok=K9R-cwuA"),
        (140, "AV DENIA AV VILLAJOYOSA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C30F2.jpg?itok=7cuPqaGB"),
        (141, "AVDA JUAN BAUTISTA LAFORA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C30F3.jpg?itok=Zw9owqJS"),
        (142, "MARTIRES DE LA LIBERTAD", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C20F2.jpg?itok=fcEJrssh"),
        (143, "C PORTUGAL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C20F3.jpg?itok=3OrRBIvZ"),
        (144, "ENTRADA CIUDAD", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C26F2.jpg?itok=OKPhiuP_"),
        (145, "ENTRADA CIUDAD 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C26F1.jpg?itok=cTd9qFxW"),
        (146, "SALIDA CIUDAD", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C26F3.jpg?itok=DcLbOvcl"),
        (147, "SALIDA CIUDAD 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C26F4.jpg?itok=ADbf32qa"),
        (148, "AVDA DE LAS NACIONES", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C38F2.jpg?itok=U9YORs9e"),
        (149, "VILLAJOYOSA SOL NACIENTE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C46M1.jpg?itok=YQoeb2Du"),
        (150, "AVDA COSTABLANCA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C44M2.jpg?itok=W9g50DjL"),
        (151, "CAJA DE AHORROS AV DENIA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C42F1.jpg?itok=oeMlifAA"),
        (152, "AVDA DE OVIEDO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C38F3.jpg?itok=gOUn6Lo4"),
        (153, "AVDA VICENTE HIPOLITO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C38F5.jpg?itok=YI7t6VKF"),
        (154, "AVDA PINTOR PEREZ GIL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C38F4.jpg?itok=vYzqV4tR"),
        (155, "CAJA DE AHORROS PLAYAS", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C42F2.jpg?itok=XfTmE5Hz"),
        (156, "AVDA NACIONES", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C44M1.jpg?itok=vGm55tNu"),
        (157, "VILLAJOYOSA PL ISLETA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C46M2.jpg?itok=N8ld6sCH"),
        (158, "AVDA COSTABLANCA 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C05M1.jpg?itok=dCzcU4gm"),
        (159, "C CAJA DE AHORROS", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C23M1.jpg?itok=rrjwrwai"),
        (160, "AVDA VICENTE HIPOLITO 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C23F2.jpg?itok=nepIAtOg"),
        (161, "AVDA CONDOMINA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C05F2.jpg?itok=CR2iiMAu"),
        (162, "A AMARGA ANTA MORENO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C62M2.jpg?itok=EPxZf0dx"),
        (163, "AGUA AMARGA N332", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C62M1.jpg?itok=v1GfnRa8"),
        (164, "ARCO IRIS G STEWART HOWIE", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C67M1.jpg?itok=M5DoWme2"),
        (165, "C ARCO IRIS SALIDA A31", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C67M2.jpg?itok=OVqGTH8j"),
        (166, "ARCO IRIS G STEWART HOWIE 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C67M3.jpg?itok=TxjK7AKD"),
        (167, "C MISTRAL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C68M1.jpg?itok=qdPCcibk"),
        (168, "C G STEWART HOWIE C MISTRAL", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C69M1.jpg?itok=6x1GNiU7"),
        (169, "ANT PESETA C DEL FRANCO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C70M1.jpg?itok=w_fFrzf3"),
        (170, "ROT ANT PESETA A31", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C70M2.jpg?itok=zFrmlMg_"),
        (171, "C ANT PESETA CNO VIEJO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C71M1.jpg?itok=hXb-lhSQ"),
        (172, "AVDA DEL EURO C DEL MARCO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C72M1.jpg?itok=4ko8e1yF"),
        (173, "AVDA DEL EURO C DE LA LIBRA", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C73M1.jpg?itok=pGvrNvA7"),
        (174, "ROT C ARCO IRIS G STEWART", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C67M3.jpg?itok=TxjK7AKD"),
        (175, "C G STEWART HOWIE C MISTRAL 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C69M1.jpg?itok=6x1GNiU7"),
        (176, "ROTONDA AGUA AMARGA C ANTONITA MORENO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C63M1.jpg"),
        (177, "CN340 C TORMOS 1", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C64M1.jpg"),
        (178, "CN340 C TORMOS 2", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C65M1.jpg"),
        (179, "CN340 C ANTONITA MORENO", "https://movilidad.alicante.es/sites/default/files/styles/upload_fotograma_big/public/camara/C66M1.jpg"),
    ]

    now = datetime.now(timezone.utc)
    minute = (now.minute // 5) * 5
    ts = now.strftime(f"%Y-%m-%d_%H-{minute:02d}")
    tag = f"snap-{ts}"
    print(f"Snapshot: {tag}")

    # ── CREAR RELEASE ──
    print("Creando release...")
    gh("release", "create", tag,
       "--repo", REPO,
       "--title", f"Snapshot {ts}",
       "--notes", f"Auto-generated snapshot {ts}",
       "--latest=false")

    # ── DESCARGAR FOTOS ──
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Referer": "https://movilidad.alicante.es/camaras",
    }
    ok = 0
    fail = 0
    tmp_dir = f"/tmp/cam_{ts}"
    os.makedirs(tmp_dir, exist_ok=True)

    def download_cam(cam_data):
        num, calle, url = cam_data
        num_str = str(num).zfill(3)
        filepath = os.path.join(tmp_dir, f"{num_str}.jpg")
        proxy_url = f"{PROXY}?url={requests.utils.quote(url, safe='')}"
        try:
            r = requests.get(proxy_url, headers=headers, timeout=15)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                return True, num_str
            return False, num_str
        except Exception as e:
            return False, num_str

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(download_cam, cam): cam for cam in CAMERAS}
        for future in as_completed(futures):
            success, num_str = future.result()
            if success:
                ok += 1
            else:
                fail += 1

    print(f"Descargadas: {ok} | Fallos: {fail}")

    # ── CREAR ZIP Y SUBIR 1 SOLO ARCHIVO ──
    zip_path = f"/tmp/cam_{ts}.zip"
    print("Creando zip...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in os.listdir(tmp_dir):
            if f.endswith(".jpg"):
                zf.write(os.path.join(tmp_dir, f), f)

    zip_size = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Zip: {zip_size:.1f} MB")

    print("Subiendo zip al release...")
    gh("release", "upload", tag, zip_path, "--repo", REPO, "--clobber")
    print("Upload completado")

    # ── LIMPIAR TMP ──
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.remove(zip_path)

    # ── BORRAR RELEASES ANTIGUOS (> 7 dias) ──
    print("Limpiando releases antiguos...")
    limite = now - timedelta(minutes=MINUTOS_RETENER)
    try:
        releases_json = gh("api", f"repos/{REPO}/releases", "--paginate", "--jq", ".[].tag_name")
        tags = [t.strip() for t in releases_json.strip().split("\n") if t.strip()]
        borrados = 0
        for t in tags:
            if not t.startswith("snap-"):
                continue
            try:
                date_part = t.replace("snap-", "")
                dt_release = datetime.strptime(date_part, "%Y-%m-%d_%H-%M").replace(tzinfo=timezone.utc)
                if dt_release < limite:
                    gh("release", "delete", t, "--repo", REPO, "--yes", "--cleanup-tag")
                    borrados += 1
                    print(f"  Borrado: {t}")
            except ValueError:
                pass
        print(f"Releases borrados: {borrados}")
    except Exception as e:
        print(f"  Error limpiando: {e}")

    print("Captura completada.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error general: {e}")
    finally:
        sys.exit(0)
