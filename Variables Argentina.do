cd "E:\Bases\EPH"
use "usu_individual_t123.dta", clear
***ARGENTINA

destring ch14, replace

*** Identificadora de hogar
sort codusu nro_hogar aglomerado
capture gen CODUSU=codusu
egen zidh=group(codusu nro_hogar aglomerado)
 
g idi=componente
g nomiembro = (idi==51 | idi==71)		/*Servicio doméstivo y pensionista*/

****MIEMBROS 
***IMPORTANTE: LOS PENSIONISTAS Y EL SERDOM QUEDAN COMO OTRO HOGAR EN LA VIVIENDA. O SEA, YA EN LA BASE NO SON PARTE DEL HOGAR. 
***TIENEN IGUAL CODUSU PERO DIFERENTE NRO DE HOGAR (SD: componente==51; PE: componente==71)
gen id=1
egen zmiembro=sum(id), by(zidh)

*********SEXO
gen sexo = 0 if (ch04==2)
replace sexo =1 if (ch04==1)

**EDUCACION
***CAMBIAMOS EL CRITERIO CON EL QUE VIENE CONSTRUIDO EN LA BASE.
***ANTES LOS QUE ESTABAN EN PRIMER AÑO DEL SECUNDARIO CON 0 AÑO APROBADO QUEDABAN COMO SI, AHORA COMO PC

gen niveled=nivel_ed
replace niveled=1 if (nivel_ed==7)
replace niveled=2 if (ch10==1 & (ch12==4 | ch12==5) & ch14==00)
replace niveled=4 if (ch10==1 & (ch12==6 | ch12==7) & ch14==00)

gen hpi=0 if (niveled!=9 & niveled!=.)
replace hpi=1 if (niveled==1) 

gen pc=0 if (niveled!=9 & niveled!=.)
replace pc=1 if (niveled==2) 

gen si=0 if (niveled!=9 & niveled!=.)
replace si=1 if (niveled==3)

gen sc=0 if (niveled!=9 & niveled!=.)
replace sc=1 if (niveled==4)

gen ti=0 if (niveled!=9 & niveled!=.)
replace ti=1 if (niveled==5)

gen tc=0 if (niveled!=9 & niveled!=.)
replace tc=1 if (niveled==6)

gen educr=.
replace educr=1 if (hpi==1 | pc==1 | si==1)
replace educr=2 if (sc==1 | ti==1)
replace educr=3 if (tc==1)

**********ESTADO 
rename estado estadold

gen estado=1 if (estadold==1)
replace estado=2 if (estadold==2)
replace estado=3 if (estadold==3 | estadold==4)


*****PARA LOS OCUPADOS*********************
rename cat_ocup cat_ocupold

gen cat_ocup=.
**patron
replace cat_ocup=1 if (estado==1 & cat_ocupold==1)
**cuenta propia
replace cat_ocup=2 if (estado==1 & cat_ocupold==2)
***asal 
replace cat_ocup=3 if (estado==1 & cat_ocupold==3)
****familiar no remunerado
replace cat_ocup=4 if (estado==1 & cat_ocupold==4)


****IDENTIFICACIÓN DEL SERV. DOMESTICO DIF A RAMA
**ACÁ SE PREGUNDA AD HOC. 98% SE LOS CLASIFICA COMO ASAL (por rama quedan algunos como cuenta propias)
gen serdom1=.
replace serdom1=0 if (estado==1 & pp04b1==2)
replace serdom1=1 if (estado==1 & pp04b1==1)

**CATEGORIA OCUPACIONAL
**hay casos de pp07h==0 para asalariados, los excluimos

***QUEDAN COMO CERO LOS ASAL NO REGI Y LOS NO ASAL
gen asareg=.
replace asareg=0 if (estado==1 & (cat_ocup==1  | cat_ocup==2 | cat_ocup==4))
replace asareg=0 if (estado==1 & cat_ocup==3 & pp07h==2)
replace asareg=1 if (estado==1 & cat_ocup==3 & pp07h==1)
egen zcantreg = sum(asareg), by (zidh)

***QUEDAN COMO CERO LOS ASAL REGI Y LOS NO ASAL
gen asanreg=. 
replace asanreg=0 if (estado==1 & (cat_ocup==1  | cat_ocup==2 | cat_ocup==4))
replace asanreg=0 if (estado==1 & cat_ocup==3 & pp07h==1)
replace asanreg=1 if (estado==1 & cat_ocup==3 & pp07h==2)
egen zcantnreg = sum(asanreg), by (zidh)

gen cuentpro=.
replace cuentpro=0 if (estado==1 & (cat_ocup==1  | cat_ocup==3 | cat_ocup==4))
replace cuentpro=1 if (estado==1 & cat_ocup==2)

gen patron=.
replace patron=0 if (estado==1 & (cat_ocup==2  | cat_ocup==3 | cat_ocup==4)) 
replace patron=1 if (estado==1 & cat_ocup==1)

gen restocup=.
replace restocup=0 if (estado==1 & (cat_ocup==1  | cat_ocup==2 | cat_ocup==3))
replace restocup=1 if (estado==1 & cat_ocup==4)

gen cuentprop=0 if (estado==1 & cat_ocup!=. & educr!=.)
replace cuentprop=1 if (estado==1 & cuentpro==1 & educr==3)

gen cuentpronp=0 if (estado==1 & cat_ocup!=.  & educr!=.)
replace cuentpronp=1 if (estado==1 & cuentpro==1 & (educr==1 | educr==2))

gen asal=0 if (estado==1 & cat_ocup!=.)
replace asal=1 if (estado==1 & cat_ocup==3)
egen zcantasal = sum(asal), by (zidh)

gen noasa=0 if (estado==1 & cat_ocup!=.)
replace noasa=1 if (estado==1 &  (cat_ocup==2  | cat_ocup==1 | cat_ocup==4))
egen zcantnoasal = sum(noasa), by (zidh)


*****************SECTOR
gen sector=.
*publico
replace sector=1 if (estado==1 &  pp04a ==1)
*privado y otro
replace sector=0 if (estado==1 & (pp04a ==2 | pp04a ==3))

********TAMAÑO ESTABLECIMIENTO
gen tam=.
*hasta 5
replace tam=1 if  (estado==1 & (pp04c>=1 & pp04c<6) | (pp04c==99 & pp04c99==1))
*6 a 40
replace tam=2 if  (estado==1 & (pp04c>=6 & pp04c<=8) | (pp04c==99 & pp04c99==2))
*mas de 40
replace tam=3 if  (estado==1 & (pp04c>8 & pp04c<=12) | (pp04c==99 & pp04c99==3))
****PARA EL SERDOM1 NO CLASIFICADO ANTES
replace tam=1 if  (estado==1 & serdom1==1 & tam==.)

***GENERAMOS INDICADORA PARA TAMAÑO DE ESTABLECIMIENTO
gen tam1 =0 if (tam!=.)
replace tam1=1 if (tam==1)

gen tam2 =0 if (tam!=.)
replace tam2=1 if (tam==2)

gen tam3 =0 if (tam!=.)
replace tam3=1 if (tam==3)

***********SECTOR INFORMAL/SECTOR FORMAL
**IMPORTANTE: VERIFICAR QUE POR DEFIN TODOS LOS NO ASAL PERTENECEN AL SECTOR PRIVADO
***sector informal
g secinfor=0 if (estado==1 & cat_ocup!=.)
replace secinfor=. if (asal==1 & sector==.)
replace secinfor=. if (asal==1 & sector==0 & tam==.)
replace secinfor=. if (cuentpro==1 & educr==.)
replace secinfor=. if (patron==1 & tam==.)
**asal priv y patron en menores a 5 ocup
replace secinfor=1 if  (estado==1 &  asal==1 & tam==1 & sector==0)
replace secinfor=1 if  (estado==1 & patron==1 & tam==1)
***cuenta propia no profes
replace secinfor=1 if  (estado==1 & cuentpro==1 & (educr==1 | educr==2))
***fliar
replace secinfor=1 if  (estado==1 & restocup==1)
****ser domestico
replace secinfor=1 if  (estado==1 & serdom1==1)

***sector formal
g secfor=0 if (estado==1 & cat_ocup!=.)
replace secfor=. if (asal==1 & sector==.)
replace secfor=. if (asal==1 & sector==0 & tam==.)
replace secfor=. if (cuentpro==1 & educr==.)
replace secfor=. if (patron==1 & tam==.)
***sector publico
replace secfor=1 if  (estado==1 & sector==1)
**asal priv y patron en mayores a 5 ocup
replace secfor=1 if  (estado==1 & asal==1 & (tam==2 |tam==3) & sector==0)
replace secfor=1 if  (estado==1 & patron==1 & (tam==2 |tam==3))
***cuenta propia profes
replace secfor=1 if (estado==1 & cuentpro==1 & educr==3)
***excluyo fliar
replace secfor=0 if (estado==1 & restocup==1)
****excluyo ser dom
replace secfor=0 if (estado==1 & serdom1==1)

***************EMPLEO INFORMAL/FORMAL
**informales
g informal=0 if (estado==1 & cat_ocup!=.)
replace informal=. if (asal==1 & asareg!=1 & asanreg!=1)
replace informal=. if (cuentpro==1 & educr==.)
replace informal=. if (patron==1 & tam==.)
***cuenta y patron informales (igual que en el sector informal)
replace informal=1 if (estado==1 & cuentpro==1 & (educr==1 | educr==2))
replace informal=1 if (estado==1 & patron==1 & tam==1)
***asal no registrado
replace informal=1 if (estado==1 & asanreg==1)
***fliar
replace informal=1 if (estado==1 & restocup==1)

***formales
g formal=0 if (estado==1 & cat_ocup!=.)
replace formal=. if (asal==1 & asareg!=1 & asanreg!=1)
replace formal=. if (cuentpro==1 & educr==.)
replace formal=. if (patron==1 & tam==.)
***cuenta y patron formales (igual que en el sector formal)
replace formal=1 if (estado==1 & cuentpro==1 & educr==3)
replace formal=1 if (estado==1 & patron==1 & (tam==2 |tam==3))
***asal registrado
replace formal=1 if (estado==1 & asareg==1)
***excluyo fliar
replace formal=0 if (estado==1 & restocup==1)

****CHEQUEOS IMPORTANTES. VERIFICAR QUE DEN BIEN
**tienen que coincidir los noasal con ambar clasif
ta secfor formal if (noasa==1), m
ta secinfor informal if (noasa==1), m

***controlo que estén clasificados sólo una vez
ta secfor secinfor if (noasa==1), m
ta secfor secinfor if (asal==1), m

ta formal informal if (noasa==1), m
ta formal informal if (asal==1), m

ta formal asareg if (asal==1), m
ta informal asanreg if (asal==1), m


****INTENSIDAD HORARIA DE OCUP PPAL
***quedan como missing los que no trabajaron en la semana

gen intenhor=. 
***subocup voluntario
replace intenhor=1 if (estado==1 & horas<35 & pp03g==2)
***subocup involuntario
replace intenhor=2 if (estado==1 & horas<35 & pp03g==1)
****ocup pleno
replace intenhor=3 if (estado==1 & horas>=35 & horas<=45)
****sobreocup
replace intenhor=4 if (estado==1 & horas>45 & horas!=.)

gen inten=.
replace inten=1 if (intenhor==1 | intenhor==2)
replace inten=2 if (intenhor==3)
replace inten=3 if (intenhor==4)

gen inten1=0 if (inten!=.)
replace inten1=1 if (inten==1)

gen inten2=0 if (inten!=.)
replace inten2=1 if (inten==2)

gen inten3=0 if (inten!=.)
replace inten3=1 if (inten==3)

gen partime=0 if (intenhor==1 | intenhor==3 | intenhor==4)
replace partime=1 if (intenhor==2)

*incluimos en part-time a los voluntarios
gen partimet=0 if (intenhor==3 | intenhor==4)
replace partimet=1 if (intenhor==2 | intenhor==1)


***CALIFICACION DEL PUESTO
*5TO DIGITO
*1 Profesional
*Tecnicos
*Operarios
*No calificado
*if ano4==2020 {
gen pp04d_v=pp04d_cod
gen pp04d=string(pp04d_v)
*}

generate str1 calif5 = substr(pp04d,5,5)

gen calif=.
replace calif=1 if (estado==1 & calif5=="1")
replace calif=2 if (estado==1 & calif5=="2")
replace calif=3 if (estado==1 & calif5=="3")
replace calif=4 if (estado==1 & calif5=="4")


***********INGRESO OCUPACIÓN PRINCIPAL, ING MONETARIOS HABITUALES
*NO SE IMPUTAN MAS. Decil 12/13 sin respuesta 

***P21 SE COMPONE:
*PARA ASAL: pp08d1+pp08f1+pp08f2 (no incluye componentes no habituales) 
*PARA NO ASAL: pp06c+pp06d (monto global, habitual y no habitual)

gen p21old=p21
drop p21
gen p21=p21old if (estado==1 &  decocur<11 & p21old!=. & p21old!=-9)
replace p21=0 if (estado==2 | estado==3)

gen inghora=p21/(horas*4.33) if (estado==1 & p21>0 & horas!=. & decocur<11)

*****INGRESOS DE OTRAS OCUPACIONES (usamos rsum porque sólo anula missing en el ingreso laboral de la ocupación principal; entonces si tienen missing lo consideramos 0)
replace tot_p12 = . if (tot_p12<0)
egen ysec=rsum(tot_p12)
replace ysec=0 if (estado==2 | estado==3)


*MIGRANTE
gen migrante=0
replace migrante=1 if (ch15==4 | ch15==5) 
