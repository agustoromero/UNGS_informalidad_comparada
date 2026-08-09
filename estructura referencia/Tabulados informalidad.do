**cuadro estructura
gen estructura=0
replace estructura=1 if cuentprop==1 & estado==1
replace estructura=2 if asal==1 & sector==0 & (tam==2 |tam==3) & serdom1!=1 & estado==1
replace estructura=3 if asal==1 & sector==1 & estado==1
replace estructura=4 if patron==1 & (tam==2 |tam==3) & estado==1
replace estructura=5 if patron==1 & tam==1 & estado==1
replace estructura=6 if asal==1 & sector==0 & tam==1 & serdom1!=1 & estado==1
replace estructura=7 if cuentpronp==1 & estado==1
replace estructura=8 if restocup==1 & estado==1
replace estructura=9 if serdom1==1 & estado==1

tab estructura if estado==1, m // quedan en cero los que no tienen información de tamaño del establecimiento

tab estructura if estado==1 & estructura>0 [fw=pondera]

*PERFILES
*jóvenes
gen menor25=0 if (ch06!=.)
replace menor25=1 if (ch06<25 & ch06!=.)

tab estructura menor25 if estado==1 & estructura>0 [fw=pondera]

*mujeres
tab estructura sexo if estado==1 & estructura>0 [fw=pondera]

*migrantes
tab estructura migrante if estado==1 & estructura>0 [fw=pondera]

*ASALARIADOS
tab asal sector if estado==1 & asal==1 & secfor==1 [fw=pondera]
tab asal sector if estado==1 & asal==1 & secinfor==1 [fw=pondera]
tab asal if estado==1 [fw=pondera]

*características contratos
*sector 1 = público
	tab tempor sector if estado==1 & estructura>0 & asal==1 & secfor==1 [fw=pondera]

tab tempor if estado==1 & estructura>0 & asal==1 & secinfor==1 [fw=pondera]

*aportes
tab asareg sector if estado==1 & estructura>0 & asal==1 & secfor==1 [fw=pondera]

tab asareg secinfor if estado==1 & estructura>0 & asal==1 [fw=pondera]

*jornada 1=subocupados | 3=sobreocupados
tab estructura inten if estado==1 & estructura>0 [fw=pondera]

*más de una ocupación
gen pluri=0 if estado==1
replace pluri=1 if ysec>0 & ysec<. & estado==1 

tab estructura pluri if estado==1 & estructura>0 [fw=pondera]

*aportes propios
tab estructura pp07i if estado==1 & estructura>0 [fw=pondera]

*ingresos

table estructura if estado==1 & estructura>0 [fw=pondiio], c(mean inghora median inghora)

table estado if estado==1 & estructura>0 [fw=pondiio], c(mean inghora median inghora)
table secfor if estado==1 & estructura>0 [fw=pondiio], c(mean inghora median inghora)
table secinfor if estado==1 & estructura>0 [fw=pondiio], c(mean inghora median inghora)


table estructura if estado==1 & estructura>0 [fw=pondiio], c(mean p21 median p21)

table estado if estado==1 & estructura>0 [fw=pondiio], c(mean p21 median p21)
table secfor if estado==1 & estructura>0 [fw=pondiio], c(mean p21 median p21)
table secinfor if estado==1 & estructura>0 [fw=pondiio], c(mean p21 median p21)
