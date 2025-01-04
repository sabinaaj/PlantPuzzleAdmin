# PlantPuzzle Admin - webová aplikace pro botanický park UJEP
Tato aplikace slouží jako administrativní rozhraní pro mobilní aplikaci, která je vyvinuta za účelem popularizace edukačních aktivit v botanickém parku UJEP. Prostřednictvím této webové aplikace mohou uživatelé přidávat nové pracovní listy, spravovat školy, návštěvníky, a sledovat jejich výsledky. Mobilní aplikace umožňuje návštěvníkům pracovat s těmito listy a zároveň nabízí gamifikované prvky, jako jsou žebříčky a odznaky pro zvýšení atraktivity.

## Diagramy a náhledy

### Rich Picture Diagram
Tento diagram vizualizuje hlavní funkce a interakce mezi uživateli, mobilní aplikací a administrativním rozhraním.

![Rich Picture Diagram](diagrams/rich_picture.jpg?raw=true)

### ERD - Schéma databáze
ERD diagram ukazuje vztahy mezi entitami v databázi, jako jsou pracovní listy, školy, návštěvníci a výsledky.


![ERD Diagram](diagrams/erd_diagram.png?raw=true )


### Diagram komponent
Tento diagram znázorňuje architekturu systému PlantPuzzle a propojení mezi jeho hlavními komponentami. Webová aplikace se skládá ze dvou základních komponent: GUI (Frontend) a Backend. Backend poskytuje rozhraní pro GUI a poskytuje ji data. Backend dále komunikuje s Mobilní aplikací prostřednictvím rozhraní, což umožňuje synchronizaci dat. Pro komunikaci používá REST API.

![Diagram Komponent](diagrams/component.png?raw=true )


### Diagram aktivit
Diagram aktivit popisuje průchod uživatele mobilní aplikací od zapnutí aplikace skrz vyplňování pracovních listů.

![Diagram Aktivit](diagrams/activity.png?raw=true )


### Diagram nasazení
Diagram nasazení znázorňuje fyzickou infrastrukturu systému PlantPuzzle, který se skládá z několika klíčových komponent. Na serveru v dockeru poběží několik kontejnerů. Jeden z nich je databáze, která uchovává všechna data a poskytuje je mobilní a webové aplikaci. Další kontejner je API server, který zajišťuje komunikaci mezi databází a mobilní aplikací pomocí REST API, a další kontejner je samotná webová aplikace pro správu pracovních listů, škol a návštěvníků. Mobilní aplikace, dostupná pro zařízení s Androidem a iOS, komunikuje s API serverem přes zabezpečené REST API a poskytuje uživatelům přístup k pracovním listům. Tento diagram přehledně ukazuje, jak jednotlivé komponenty spolupracují a kde jsou nasazeny.

![Diagram Nasazení](diagrams/deployment.png?raw=true )


### Diagram balíčků
Diagram balíčků znázorňuje strukturu aplikace PlantPuzzle a rozdělení jednotlivých funkcionalit mezi tři klíčové vrstvy: webovou aplikaci, Django backend a mobilní aplikaci. Každá vrstva obsahuje moduly Oblasti, Pracovní listy a Návštěvníci, které mezi sebou komunikují. Django backend slouží jako prostředník mezi webovou a mobilní aplikací a poskytuje REST API pro přístup k datům. Django backend má přístup k databázi a spravuje data pro webovou aplikaci a mobilní aplikaci. Moduly jsou na sobě závislé. Oblasti se starají o jednotlivé oblasti a jejich rostliny. Modul pracovní listy poskytuje funkcionalitu pro tvorbu a spravování pracovních listů. Pracovní listy spadají pod oblasti. Modul návštěvníci spravuje školy a uživatele mobilní aplikace. Také spravuje informace o výsledcích pracovních listů pro jednotlivé uživatele.

![Diagram Balíček](diagrams/package.png?raw=true )


### Náhledy z aplikace

- **Webové rozhraní**: Seznam oblastí a tvorba nových pracovních listů.


![Seznam Oblastí](diagrams/seznam_oblasti.png?raw=true )

![Vytváření Pracovního Listu](diagrams/vytvoreni_listu.png?raw=true )


- **Mobilní aplikace**: Wireframe pro připravovanou mobilní aplikaci. Na ukázce jsou různé typy úloh z pracovních listů.


![Typy Úloh 1](diagrams/typy_uloh_1.png?raw=true)

![Typy Úloh 2](diagrams/typy_uloh_2.png?raw=true )
