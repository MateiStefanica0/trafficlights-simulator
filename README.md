# Descriere
Pentru ca toti 3 traim in Bucuresti, suntem obisnuiti si constienti de cat de mult timp din viata pierdem in trafic, asa ca am incercat sa creem o aplicatie care sa permita vizualizarea traficului si implementarea a doua tipuri de semafoare: normale si inteligente. Astfel, speram noi, se poate observa cat de mult ajuta varianta din urma. Mentionam si ca timpii de asteptare ai semafoarelor, dar si "rationamentele" folosite pentu semafoarele inteligente sunt oarecum naive, in ideea in care am cautat noi niste valori care sa fie rezonabile pentru timpii de asteptare, insa intr-o implementare din viata reala acestia ar fi alesi in functie de o multitudine de studii si date despre trafic.
De asemenea, pentru ca suntem consitenti de faptul ca traficul este intr-o foarte mare masura imprevizibil si foarte dependent de diversi factori umani, am incerat sa includem cateva elemente care sa simuleze acest aspect. Astfel, vitezele masinilor sunt diferite (dar incluse dar respecta totusi un range), directiile in care o iau masinile sunt alese random, masinile au o sansa foarte mica de a se strica, moment in care apare un cerc rosu langa ele si se opresc (cu asta am vurt sa simulam si evenimente din viata reala precum accidentele), iar utilizatorul poate sa "porneasca ploaia" ceea ce le scade tuturor participantilor la trafic viteza. 
Pentru a si concretiza toate aceste lucruri si diferente dintre cele doua tipuri se semafoare, am adaugat si o functionalitate care ii permite utilizatorului sa isi aleaga un punct de plecare si de sosire, iar programul va calcula cea mai scurta ruta intre acele 2 puncte. Astfel, utilizatorul va putea si "sa faca parte din trafic" si sa observe cum este impactat de diferite lucruri care se pot intampla in trafic.
Utilizatorul are libertate completa sa genereze fluxul traficului dupa bunul plac, el alegand numarul de masini care sa se spawneze pe secunda, numarul de secunde pentru care sa se spawneze masinile, dar si locurile (spawn pointurile) de unde sa plece masinile.
Pentru a fi mai usor de tras concluzii, am adaugat si cateva statistici (numar de masini/intersectie, timp total de asteptare in intersectii, timpul in care a rulat simularea, timpul luat de vehicului ales de utilizator sa ajunga de la punctul de plecare la destinatie etc)

# Link Github:

https://github.com/MateiStefanica0/trafficlights-simulator

# Instructiuni:
Recomandam ca la prima rulare a programului sa se foloseasca comanda `make run` din root-ul proiectului, pentru a fi instalate toate dependintele si versiunile necesare de biblioteci. Dupa aceea, pentru a putea rula mai usor, se poate rula direct `python3 main.py` din folderul src
In fereastra principala a proiectului utilizatorul poate sa isi aleaga propriile setari sau sa le lase pe cele default si are 2 variante de simulare: normala sau ceva cu semafoare inteligente
!! Nu recomandam un grid mai mare de 6x6, mai mult de 5-6 masini pe secunda sau mai mult de 150-200 de masini per total, din cauza limitarilor de performanta ale PyGame, care vor face simulare sa aiba lag (mentionam ca valorile acestea sunt orientative si depind foarte mult si de ce spawnpointuri alege utilizatorul)
Diferenta dintre cele 2 simulari este, evident, tipul semafoarelor
In fereastra de simulare utilizatorul are in dreapta sus butoane de `Play/Pause`, `Reset` si `Stats`, in stanga sus butoanele de `Exit` si `Menu` (in caz ca utilizatorul vrea sa schimbe tipul simularii sau variabilele de rulare), in stanga jos butonul de `Start raining`, in dreapta jos timpii de rulare ai simularii (Total waiting time este suma tuturor timpilor de asteptare ai tuturor masinilor in intersectii) si mijloc sus butonul de `Choose a route`.
La apasarea butonului `Choose a route` se deschide o alta fereastra care ii permite utilizatorului sa aleaga spawn pointul si destinatia. Apoi, dupa ce apasa Play, vehiculul violet se spawneaza dupa ce jumatate din celelalte vehicule s-au spawnat


# Tehnologii Folosite:
Am reusit sa scriem acest proiect exclusiv in Python si am folosit cel mai mult PyGame si TKinter, dar si cateva biblioteci precum random, time, matplotlib si threading

# Contributii
Mentionam ca este primul proiect de echipa pe care l-am avut (0 experienta anterioara), asa ca mai ales la inceput a fost destul de greu sa lucram individual si sa impartim sarcinile fara sa ne incurcam. Din cauza asta am facut cu totii cate putin din toate, dar in principal atributiile au fost urmatoarele:

## Matei Stefanica
    - a incercat sa implementeze versiunea primitiva a proiectului, adica scheletul simularii de trafic (masinile care se deplaseaza si asteapta una dupa alta/la semafoare) 
        - de mentionat ca a facut asta cu ajutor din partea lui Stefan si Anastasia, care la randul lor au experimentat cu tehnologiile si au mai dat cateva sfaturi/idei
    - s-a ocupat de majortatea pull requesturilor si github in general, fiind singurul cu macar putina experienta
## Anastasia Stanciu
    - s-a ocupat de cea mai mare parte din interfata grafica (meniu principal, o mare parte din butoane, fereastra de statistici)
    - a lucrat la o mare parte din functionalitatile "de control" al traficului din cadrul simularii (ploaie, Play/Pause, timpi de rulare etc)
    - a lucrat la statistici
## Stefan Nemeti
    - initial a experimentat cel mai mult cu tehnologiile, oferindu-le celorlalti un punct de plecare solid
    - a lucrat la implementarea semafoarelor inteligente si la hitboxurile masinilor
    - a lucrat la statistici

## Comun
    - de cateva ori ne-am si vazut f2f sau am lucrat pe discord la comun, pentru a ne sfatui si a reusi sa rezolvam diferite buguri, astfel sunt destul de multe elemente care apar ca fiind de la o singura persoana, dar de fapt sunt rezulatul colaborarii tuturor celor 3 membiri
        - functionalitatea "choose a route"
        - refactorizarea codului
        - majoritatea testarii si rezolvarea problemelor aparute

# Dificultati
- una din dificultatile principale a provenit din faptul ca e primul proiect mai mare la care lucram cu github si a fost putin dificil pana am reusit sa ne dam seama cum se rezolva cel mai bine diferite probleme aparute pe parcurs
- am facut greseala de a incepe tot proiectul intr-un singur fisier, care a devenit rapid mult prea lung si nici nu am facut refactorizarea si reorganizarea lui decat la final, cand ne-am dat seama ca anumite functionalitati nu mai merg, pentru ca se bazau pe diferite constante sau variabile globale
    - a fost dificil sa rezolvam problema, mai ales ca nu am mai avut asa de mult de a face cu variabile cu diferite scope-uri in Python
- a fost destul de dificil si sa punem la punct functiile de miscare pentru "vehiculul violet", pentru ca el isi bazeaza urmatoarele miscari atat pe baza drumurilor pe care le are la dispozitie, cat si pe baza coordonatelor la care trebuie sa ajunga si a fost destul de greu sa facem asa incat sa si aleaga directia buna in intersectii, dar nici sa nu depaseaza ilegal alte masini
- ultimul, singurul bug de care stim, dar nu am reusit sa il rezolvam din cauza limitarilor TKinter, este faptul ca din cauza modului in care TKinter gestioneaza threadurile, uneori, foarte rar, cand utilizatorul apasa butonul de Exit in fereastra de statistici, apare un fel de race condition si din cauza asta nu mai functioneaza programul si trebuie oprit fortat. Din pacate pare o problema care apare cand sunt combinate TKinter, PyGame si threadingul si nu am reusit sa gasim vreo rezolvare concreta.
   
