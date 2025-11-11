import numpy as np
from element_map import elementMap
from copy import deepcopy

coef = 42.577478461/5.5856946893 #gamma/nuclear g factor # hacked for electron and neutron...
formatting = True

def loadElements(path):
    elements = []

    def printE():
        print(curE['z'], curE['abbr'], curE['name'])

        for isotope in curE['isotopes']:
            print(isotope)

        print()

    curE = {'z':0, 'abbr':'', 'name':''}
    isotopes = []

    a = open(path, 'r', errors='ignore')

    for line in a:
        if line[0] =='%':
            continue

        line = line.strip('\n')
        words = [v for v in line.split(' ') if v not in['']]

        #0 z, 1 isotope, 2 radioactive, 3 abbr, 4 name, 5 spin, 6 gamma, 7 NA, 8 Q

        curIsotopes = {'isotope': int(words[1]), 'spin': float(words[5]), 'gamma': float(words[6]), 'NA': float(words[7]), 'Q': float(words[8]), 'rad': words[2]}

        if curE['z'] != int(words[0]):
            if curE['z'] != 0:
                curE['isotopes'] = isotopes
                elements.append(curE)
                printE()

            curE = {'z':int(words[0]), 'abbr':words[3], 'name':words[4].capitalize()}
            isotopes = []

        isotopes.append(curIsotopes)

    curE['isotopes'] = isotopes
    elements.append(curE)
    printE()

    #drop exotic radioactives unless
    for e in elements:
        dropped = False

        print()
        print(e['z'], e['abbr'], len(e['isotopes']))

        for i, iso in enumerate(e['isotopes']):
            if iso['rad']=='*' and iso['NA'] == 0:
                if (
                       (e['abbr']=='H'  and iso['isotope']==3)
                    or (e['abbr']=='C'  and iso['isotope']==14)
                    or (e['abbr']=='O'  and iso['isotope']==18)
                    or (e['abbr']=='Tc' and iso['isotope']==99)
                    or (e['abbr']=='Pm' and iso['isotope']==147)
                    or (e['abbr']=='Po' and iso['isotope']==209)
                    or (e['abbr']=='Ac' and iso['isotope']==227)
                    or (e['abbr']=='Th' and iso['isotope']==229)
                    or (e['abbr']=='U'  and iso['isotope']==234)
                    or (e['abbr']=='Np' and iso['isotope']==237)
                    or (e['abbr']=='U'  and iso['isotope']==238)
                    or (e['abbr']=='Pu' and iso['isotope']==239)
                    or (e['abbr']=='Am' and iso['isotope']==243)
                   ):
                    continue

                print('dropping',e['abbr'],iso['isotope'])

                e['isotopes'].pop(i)
                dropped = True
                
        if dropped:
            print(e['abbr'],len(e['isotopes']))

    print()
    print(f'{len(elements) = }')

    #definitely a little hacky on the electron and neutron gammas...
    elements.append({'z':'','name':'Electron', 'abbr':'$\\gamma_e$', 'isotopes':[{'isotope':None, 'spin':0.5,'gamma':(28024.951/coef), 'Q':0, 'NA':100}]})
    elements.append({'z':'','name':'Neutron', 'abbr':'$\\gamma_n$', 'isotopes':[{'isotope':None, 'spin':0.5,'gamma':(-29.1646935/coef), 'Q':0, 'NA':100}]})

    for e in elements:
        if e['abbr'] == 'H':
            e0= deepcopy(e)
            e0['abbr'] = 'H_{example}'

    elements.append(e0)

    return elements


def getRows(elements, rows):
    rowMaxs = np.zeros(len(rows), dtype=np.int64)

    for r, row in enumerate(rows):
        rowMax = 0

        print()

        for e in row:
            print(e, elements[e-1]['abbr'], len(elements[e-1]['isotopes']))

            if len(elements[e-1]['isotopes']) > rowMax:
                rowMax = len(elements[e-1]['isotopes'])

        rowMaxs[r] = rowMax

    rowMaxs += 2

    print()
    print(rowMaxs)

    return rowMaxs


def generateTable(elements, maxRows, rows):
    allRows = np.sum(maxRows)
    allCols = 18 #isotope, spin, gamma, q, na

    table = [[' & & & & & & ']*(allCols-1) +[' & & & & &'] for i in range(allRows)]

    print(f'table {len(table)}x{len(table[0])}')

    return table


def populateTable(table, elements, maxRows, rows):
    #5 colums per element
    #18 elements per row
    print()

    for e in elements:
        r0, c0, color = elementMap(e['abbr'])
        r1 = int(np.sum(maxRows[:r0]))

        if color != '\\other':
            colCom = formatting*(f'\\cellcolor{{{color}}}')
        else:
            colCom = ''

        isC0 = formatting*((c0==0 and e['abbr'] != '$\\gamma_e$') or (e['abbr'] in ['La', 'Ac']))

        print(e['abbr'], c0,r0,r1 )

        if e['abbr'] == 'H_{example}':
            e['abbr'] = 'H'

        if e['abbr'] in ['$\\gamma_e$', '$\\gamma_n$']:
            table[r1][c0] =  ('\\multicolumn{1}{|l}{'  + colCom + formatting*'\\zFont{\\textbf{'   + f'{e["z"]}' + formatting*'}}' + '}  & '
                              +'\\multicolumn{4}{l|}{' + colCom + formatting*'\\nameFont{' + e['name']  + formatting*'}' + '}  & ' + (c0<17)*' & ')
            table[r1+1][c0] = '\\multicolumn{5}{|c|}{' + isC0*'\\Gape[1cm][1cm]{' + colCom + formatting*'\\abbrFont{' + e['abbr']  + formatting*'}' + isC0*'}' + '}  & ' + (c0<17)*' & '
        else:
            zText = colCom + formatting*'\\zFont{\\textbf{' + f'{e["z"]}' + formatting*'}}'
            nameText = colCom + isC0*'\\Gape[\\nameGape][0cm]{' + formatting*'\\nameFont{' + e['name']  + formatting*'}' + isC0*'}'

            table[r1][c0] =  zText + '&' +'\\multicolumn{4}{l}{' + nameText + '} & ' + (c0<17)*' & '
            table[r1+1][c0] = '\\multicolumn{5}{c}{' + isC0*'\\Gape[\\abbrGap][\\abbrGap]{'+ colCom + formatting*'\\abbrFont{' + e['abbr']  + formatting*'}' + isC0*'}' + '}  & ' + (c0<17)*' & '

        if e['abbr'] not in ['$\\gamma_e$', '$\\gamma_n$']:
            print('element',e['abbr'], 'will have', maxRows[r0]-2, 'rows')

            for i in range(maxRows[r0]-2):
                if i < len(e['isotopes']):
                    isotope = e['isotopes'][i]

                    nucleons = repr(e['isotopes'][i]['isotope'])

                    NA = colCom

                    if isotope['NA'] == 0:
                        NA += '0'
                    elif isotope['NA'] < 0.1:
                        NA +=  '$\\ll$1'
                    elif isotope['NA'] < 1:
                        NA +=  '$<$1'
                    else:
                        NA +=  colCom +repr(round(isotope['NA']))

                    if isotope["spin"] == 0:
                        spin = colCom + ' '
                        gamma = colCom + ' '
                        Q = colCom + ' '
                    else:
                        if isotope["spin"] == 0.5:
                            spin = '1/2'
                        elif isotope["spin"]%1 == 0.5:
                            spin = colCom + f'{int(isotope["spin"]*2)}/2'
                        else:
                            spin = colCom + f'{int(isotope["spin"])}'

                        gamma = colCom + repr(round(isotope['gamma']*coef, 1))

                        Q = colCom

                        if isotope['Q'] == 0:
                            Q += ' '
                        else:
                            Q += repr(round(isotope['Q']*1000))
                else:
                    spin = colCom + ' '
                    gamma = colCom + ' '
                    Q = colCom + ' '
                    NA = colCom + ' '
                    nucleons = ' '

                table[r1+2+i][c0] = f'{colCom} {nucleons} & {spin} & {gamma} & {Q} & {NA} & ' + (c0<17)*'&'
        else:
            table[r1+i][c0] =  '\\multicolumn{1}{|l}{} & 1/2 & \\multicolumn{3}{l|}{' + repr(round(e['isotopes'][0]['gamma']*coef,1)) + '} & & '

        if e['abbr'] in ['He', 'Ne','Ar','Kr','Xe','Rn','Lu','Lr']:
            table[r1+maxRows[r0]-1][c0] += '\\\\'
        if e['abbr'] in ['Og']:
            table[r1+maxRows[r0]-1][c0] += '\\\\ \\Gape[2cm][1cm]{ } \\\\ \\cline{1-5} \\cline{7-11}'

    #"""
    for c in range(1,17):
        table[1][c] = ' '

    table[1][1] = '\\multicolumn{95}{c}{' + formatting*'\\titlFont{' + 'Periodic Table For Magnetic Resonance' + formatting*'}' +'} & &'

    for c in range(5,12):
        table[5][c] = ' '

    table[5][5] = ( '\\multicolumn{42}{l}{\\multirow{5}{=}{'
                    + formatting*'\\capFont\\fontfamily{lmss}\\selectfont'
                    + '\\shortstack[l]{'
                    + 'Magnetic resonance data primarily from EasySpin.org:\\\\'
                    + '$\\,\\,\\,\\,$https://easyspin.org/documentation/isotopetable.html\\\\'
                    + 'Sources:\\\\'
                    + '$\\,\\,\\,\\,$Table of Nuclear Magnetic Dipole and Electric Quadrupole Moments, N.Stone (2014)' + '\\\\'
                    + '$\\,\\,\\,\\,$Table of Nuclear Quadrupole Moments, N.Stone, (2013)\\\\'
                    + '$\\,\\,\\,\\,$Table of the Isotopes, N.E.Holden\\\\'
                    + '$\\,\\,\\,\\,$Nuclear Quadrupole Moments, P.Pyykk\\"{o}, (2008)\\\\'
                    + 'Uncertainties at high atomic numbers can exceed 10 percent.\\\\'
                    + 'Send corrections to Michael W. Malone: mwmalone@gmail.com\\\\'
                    + 'https://github.com/spyctra/Magnetic-Resonance-Periodic-Table'
                    + '}}} & ')

    addendum  = '\\end{tabular} \n'

    if formatting:
        """
        #Useful for finding tikz coordinates
        addendum +='\\begin{tikzpicture}[remember picture,overlay,scale=1] \n'
        addendum +='\\tikzset{shift={(-32.5in,-12)}}                       \n'
        addendum +='\\draw[help lines] (0,0) grid (3,2);                   \n'
        addendum +='\\draw[->,red,very thick] (0in,0in) -- (10in,10in);    \n'
        addendum +='\\draw[->,red,very thick] (0in,0in) -- (-10in,10in);   \n'
        addendum +='\\draw[->,red,very thick] (0in,0in) -- (-10in,-10in);  \n'
        addendum +='\\draw[->,red,very thick] (0in,0in) -- (10in,-10in);   \n'
        addendum +='\\draw[->,red,very thick] (-8in,-0in) -- (-8in,8in);   \n'
        addendum +='\\end{tikzpicture}   \n'
        #"""

        f = open('./MR_table_footer.txt','r')
        for line in f:
            addendum += line

    addendum +='\\end{document}                                                   \n'
    addendum += '\n'

    for e in elements:
        if e['abbr'] == 'Lu':
            r0, c0, color = elementMap(e['abbr'])
            r1 = int(np.sum(maxRows[:r0]))

            table[r1+2][17] += '\\\\ \\cline{1-5} \\cline{7-11}'
    #"""

    a = open('./MR_latex_table.tek', 'w')

    h = open('./MR_table_header.txt', 'r')

    for line in h:
        a.write(line)

    for row in table:
        row = ''.join(row)

        if 'cline' not in row:
            a.write(row+'\\\\ \n')
        else:
            a.write(row+'\n')

    a.write(addendum)
    a.close()


def main():
    rows = [ [1,2]
            ,[i for i in range(3,11)]
            ,[i for i in range(11,19)]
            ,[i for i in range(19,37)]
            ,[i for i in range(37,55)]
            ,[55,56] + [i for i in range(72,87)]
            ,[87,88] + [i for i in range(104,119)]
            ,[i for i in range(57,72)]
            ,[i for i in range(89,104)]
           ]

    elements = loadElements('./easyspinDatabase_2025-10-27.txt')
    maxRows = getRows(elements, rows)
    table = generateTable(elements, maxRows, rows)
    populateTable(table, elements, maxRows, rows)


if __name__ == '__main__':
    main()


