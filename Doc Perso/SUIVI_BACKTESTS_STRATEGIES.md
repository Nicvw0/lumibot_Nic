# Suivi des backtests des stratégies du mini-fonds

Journal central des hypothèses, expériences et décisions de recherche.
Last Updated : 2026-10-30
Status : Préparation — aucun backtest de stratégie actions S&P 500 lancé dans ce journal.
Audience : Propriétaire du mini-fonds et intervenants chargés des recherches.

## Overview

Objectif : identifier une stratégie prometteuse sur actions individuelles du S&P 500, puis qualifier son exécution avant Paper et Live. Ce journal référence les résultats réels et leurs preuves ; il ne remplace ni les rapports natifs LumiBot ni le code versionné.

Sources du programme :
- [Stratégies proposées et recherches](strategies_trading_mini_fonds_lumibot.md).
- [Synthèse de l’audit et réserves](synthese_audit_strategies_lumibot.md).
- [Plan principal](plan_mini_fonds_lumibot.md), phases B et C.
- [Workflow et horaires validés](WORKFLOW_QUOTIDIEN_MINI_FONDS.md), sections 15 et 16.

Les mentions « horaires à définir » dans les anciens documents sont dépassées par le workflow : les horaires sont maintenant validés. Aucune stratégie concrète n’est encore enregistrée dans le catalogue de l’application.

## 1. Cadre de comparaison

- Actions individuelles du S&P 500 ; SPY peut servir de référence ou d’indicateur, pas de position cible.
- Utiliser la composition de l’indice à chaque date historique, avec les sorties, événements et données nécessaires. La liste actuelle GitHub ne suffit pas à un test historique fiable.
- Univers admissible préparé avant séance, selon les critères définis avant le test. Ne pas effacer silencieusement les entreprises dont les données sont difficiles à obtenir.
- Quatre moments : 9 h 00, 10 h 15, 12 h 45, 15 h 30 en America/New_York. Pour une clôture à 13 h : 9 h 00, 10 h 15, 11 h 15, 12 h 30.
- Les moments peuvent conclure à conserver ou ne rien faire. Ils ne forcent ni transactions ni rééquilibrages.
- Un premier test de signal sur barres quotidiennes reste possible s’il est identifié comme tel : il ne qualifie pas les quatre moments intrajournaliers. Ne pas fabriquer quatre prix avec une seule barre quotidienne.
- Garde-fou cash : `disabled` pour l’exploration actuelle. Mesurer cash négatif et financement implicite ; ne pas présenter le résultat comme sans emprunt.
- Reprendre le moteur, les indicateurs, les données, les ordres et les rapports LumiBot existants. Adapter une variante personnelle sans modifier l’exemple original.
- La période 2021–2025 est déjà examinée : elle reste exploratoire. Les nouvelles périodes de conception, validation et test final doivent être fixées avant ajustement ; aucune période n’est automatiquement hors échantillon.
- Les règles, données, frais, dividendes, ajustements et conventions du benchmark doivent être cohérents entre candidats.
- Aucun backtest, appel IA facturé, ordre Paper/Live ou commit n’est déclenché par ce document.

## 2. Registre des candidats

Les identifiants STR désignent les hypothèses ; les identifiants BT désigneront leurs exécutions. Une stratégie peut donner lieu à plusieurs expériences conservées séparément.

| ID | Candidat | Priorité | Statut initial |
|---|---|---|---|
| STR-01 | Momentum relatif sur actions | 1 | Protocole à définir |
| STR-02 | Suivi de tendance sur actions | 2 | Protocole à définir |
| STR-03 | Momentum avec filtre de tendance du marché | 3 | Comparaison conditionnée aux références STR-01/02 |
| STR-04 | Breakout d’ouverture | Conditionnelle | Faisabilité intraday à vérifier |
| STR-05 | Retour à la moyenne | Ultérieure | Adaptation actions à étudier |
| STR-06 | Qualité / valorisation | Ultérieure | Données fondamentales datées à vérifier |

### STR-01 — Momentum relatif

**Hypothèse :** un classement des performances passées pourrait sélectionner des actions présentant une persistance relative, après coûts.

**Existant :** `lumibot/example_strategies/stock_momentum.py`, exemple Python sur trois ETF, une position, fenêtre de deux jours et réévaluation toutes les deux séances.

**À définir avant test :** horizon, éventuelle exclusion des derniers jours, nombre de positions, pondérations, fréquence de rééquilibrage, critères de sortie et traitement des changements d’univers. Aucun de ces paramètres n’est validé par défaut.

**Comparaison :** référence S&P 500/SPY documentée ; mesure du risque, de la concentration et de la rotation en plus du rendement.

**Réserves :** l’exemple original ne représente pas un portefeuille multi-actions ; vérifier les positions après exécution et la gestion des refus. Le réglage de deux jours n’est pas un choix acquis.

**Prochaine étape :** préparer un protocole reproductible avec l’univers et les données historiques effectivement disponibles.

### STR-02 — Suivi de tendance

**Hypothèse :** des règles de tendance sur chaque titre pourraient améliorer le profil rendement/risque, notamment en réduisant certaines phases de baisse.

**Existant :** `SMAIndicator` dans `lumibot/indicators/builtin.py` et `lumibot/example_strategies/ai_researcher_trader.py`.

**Distinction :** l’indicateur est un composant Python ; l’exemple est une équipe IA sur un symbole utilisant une moyenne de 20 barres. Ni l’un ni l’autre ne constitue notre stratégie validée.

**À définir avant test :** signal d’entrée et de sortie, période des indicateurs, sélection et pondération des titres, fréquence de décision. Distinguer tendance du titre et filtre global du marché.

**Comparaison :** mêmes conditions que STR-01 ; mesurer aussi faux signaux, périodes sans position et reprises manquées.

**Prochaine étape :** décrire une première règle explicite, sans multiplier les indicateurs ou ajouter une IA uniquement parce qu’elle existe.

### STR-03 — Momentum + filtre de tendance du marché

**Hypothèse :** un filtre de régime appliqué à STR-01 pourrait réduire certains drawdowns, au prix d’expositions ou de reprises manquées.

**Existant :** assemblage à construire à partir de STR-01 et des composants de tendance. Aucun mini-fonds combiné prêt à l’emploi identifié.

**À définir avant test :** indicateur de marché, règle de filtre, réduction ou sortie, condition de retour et interaction avec les positions existantes.

**Comparaison essentielle :** même Momentum, mêmes paramètres et mêmes données, avec puis sans ce seul filtre. STR-02 fournit une référence complémentaire ; ne pas confondre son signal par titre avec le filtre global.

**Prochaine étape :** tester seulement après avoir établi la référence STR-01 ; ne pas modifier simultanément classement, allocation et filtre.

### STR-04 — Breakout d’ouverture

**Hypothèse :** une rupture d’une plage initiale de cotation pourrait produire des opportunités intraday après frictions.

**Existant :** `lumibot/example_strategies/ai_opening_range_breakout.py`, exemple IA avec range 9 h 30–9 h 45 et contrôles horaires, sur actions et ETF.

**À définir avant test :** construction du range, confirmation, entrées, sorties, stops, positionnement, durée maximale et traitement des mouvements déjà survenus.

**Condition préalable :** disponibilité d’historiques intraday appropriés, prix et frais réalistes, gestion effective des ordres de protection entre les cycles.

**Compatibilité horaire :** notre cycle après ouverture est à 10 h 15 ; un signal intervenu à 9 h 45 n’est pas un ordre exécutable rétrospectivement à 9 h 45. Tester une entrée à partir de 10 h 15 ou soumettre explicitement une adaptation du protocole. Ne pas changer les quatre horaires sans décision.

**Réserves :** l’étude citée dans le document des stratégies porte sur une autre variante, notamment un range de cinq minutes et un univers plus large. Ses résultats ne sont pas transférables à notre exemple de quinze minutes.

**Prochaine étape :** étude de faisabilité ; pas de priorité sur Momentum et tendance.

### STR-05 — Retour à la moyenne

**Hypothèse :** certaines déviations temporaires pourraient être suivies d’un retour vers une référence, après coûts.

**Existant :** `lumibot/example_strategies/ccxt_backtesting_example.py`, exemple Python crypto à bandes de Bollinger ; composants Bollinger et RSI disponibles.

**À définir avant test :** adaptation aux actions, référence et fenêtre, seuils, entrées/sorties, invalidation en tendance persistante, durée et dimensionnement.

**Comparaison :** résultat après rotation et frais ; sensibilité aux périodes de tendance forte et aux pertes extrêmes.

**Réserves :** l’exemple crypto n’est pas une stratégie actions validée. La disponibilité de plusieurs indicateurs ne justifie pas leur empilement.

**Prochaine étape :** protocole distinct ultérieur, avec une hypothèse unique.

### STR-06 — Qualité / valorisation

**Hypothèse :** des critères financiers de qualité et/ou de valorisation pourraient améliorer la sélection à horizon plus long.

**Existant :** `ai_trading_team_warren_buffett_value.py` et `ai_trading_team_bill_ackman_concentrated.py` dans `lumibot/example_strategies/`.

**À définir avant test :** qualité et valorisation comme facteurs distincts ou combinaison explicite, critères, publications prises en compte, délai de disponibilité, sélection, poids et cadence.

**Comparaison :** portefeuille de référence approprié, concentration sectorielle, rotation et exposition aux facteurs.

**Réserves :** exemples IA guidés par prompts, pas facteurs quantitatifs déjà validés. Utiliser les informations publiées à l’époque, pas les fondamentaux actuels ou des révisions ultérieures.

**Prochaine étape :** vérifier la disponibilité et les dates des données fondamentales avant adaptation.

## 3. Expériences transversales — ne pas confondre avec une stratégie

### EX-01 — Financement et exécution d’une candidate

Correspond à la variante D du document des stratégies.

Après sélection d’une candidate prometteuse : adapter dimensionnement et gestion des refus, puis comparer les modes de financement selon un protocole explicite. Un changement de code et de mode simultané ne permet pas d’attribuer tout l’effet au seul garde-fou. Le rejeu existant de Momentum avec nombreux refus illustre ce problème.

Examiner réservations de cash, prix d’exécution, ordres en cours, exécutions partielles, annulations et doublons. Les modes `cash` et `margin` ne sont pas activés par ce journal.

### EX-02 — Apport des agents IA

Référence d’organisation : `ai_trading_team_bull_bear_large_cap_stocks.py`, recherche → arguments favorables → objections → décision.

Cette mécanique n’est pas une stratégie économique. Évaluer son apport séparément, si utile, sur une référence déjà définie : avec/sans revue IA, mêmes contraintes, coûts et données disponibles. Journaliser modèle, instructions, outils, coûts, erreurs et éventuel rejeu de cache. Les propositions sont validées en Python ; aucun agent de trading direct n’est ajouté.

### Autres composants

VWAP, RSI, Bollinger, filtres macro, stops, brackets et rééquilibrage sont des outils ou mécanismes complémentaires. Ils ne deviennent pas automatiquement des candidats séparés. Ouvrir une nouvelle hypothèse documentée si leur rôle économique doit être testé. Les rotations ETF et les exemples sectoriels ETF ne sont pas notre univers cible.

## 4. Méthode et décisions

1. Choisir une hypothèse et rédiger la fiche avant de coder ou lancer.
2. Fixer paramètres, données, coûts, périodes et critères de décision. Les seuils numériques restent à décider, ils ne sont pas inventés ici.
3. Vérifier la faisabilité des données et de l’horloge. Si l’univers historique manque, marquer le test exploratoire biaisé ou bloqué, pas validé.
4. Exécuter avec un identifiant unique ; conserver configuration et rapports.
5. Contrôler la validité des résultats : trous de données, positions, ordres, cash et cohérence des métriques.
6. Rejouer la même configuration pour la reproductibilité. Une réponse IA mise en cache n’est pas une répétition indépendante du raisonnement.
7. Comparer une modification logique à la fois, conserver les échecs et comptabiliser toutes les variantes essayées.
8. Étudier robustesse, coûts plus défavorables et paramètres voisins avant sélection. Ne pas choisir au seul rendement maximal.
9. Réserver un test final réellement non utilisé pour les réglages ; après consultation, il ne reste plus vierge.
10. Conclure : poursuivre, modifier l’hypothèse, rejeter ou bloquer pour manque de preuves. Aucune promotion automatique vers le live.

Statuts d’une expérience : PRÉPARATION, PRÊTE, EN COURS, TERMINÉE À AUDITER, EXPLOITABLE, INVALIDE ou BLOQUÉE.
« Exploitable » signifie que les résultats peuvent être analysés, pas que la stratégie est rentable ou autorisée en réel.

## 5. Registre des nouvelles expériences

Identifiant : `BT-0001`, puis numérotation croissante. Ne jamais réutiliser un identifiant ; un rejeu reçoit son propre identifiant et référence l’original.

**Aucune nouvelle expérience lancée à ce jour.** La première fiche et ses critères doivent être remplis avant le premier test. Une ligne sera ajoutée ici à chaque lancement.

| ID | Candidat | Variation / hypothèse | Période | Statut | Conclusion | Preuves |
|---|---|---|---|---|---|---|
| — | — | Aucun test lancé | — | — | — | — |

## 6. Modèle de fiche d’expérience

### BT-XXXX — Titre à renseigner

**Avant lancement**

- Candidat STR ou expérience EX :
- Date de préparation et responsable :
- Statut :
- Question et hypothèse vérifiable :
- Expérience de référence et modification unique :
- Critères d’acceptation, de rejet et d’invalidation, avec seuils choisis avant calcul :
- Code : fichiers, révision Git si disponible, empreintes des fichiers modifiés non commités :
- Versions Python, LumiBot et dépendances pertinentes :
- Paramètres exacts, configuration et commande reproductible, sans identifiants secrets :
- Univers : source, composition historique, règles d’admissibilité et exclusions :
- Données : fournisseur, flux, granularité, couverture, historique préalable, instant de disponibilité :
- Période : début inclus, fin exclusive, fuseau, rôle conception/validation/test final :
- Calendrier et cycles : quatre moments configurés ou étude quotidienne de signal uniquement :
- Capital initial, positions initiales et devise :
- Frais, spread, glissement, modèle de prix/remplissage et limites connues :
- Splits, dividendes, prix ajustés/non ajustés et mode de crédit des dividendes :
- Guard cash et plafond éventuel ; hypothèses de financement et intérêts :
- Benchmark et convention prix/rendement total, traitement des dividendes et coûts :
- Si IA : modèle, version disponible, prompts, schéma, outils, dates des preuves, mémoire isolée, cache et budget :

**Après exécution**

- Début/fin réelle de l’exécution et durée :
- Période effectivement couverte ; séances/barres attendues et observées :
- Statut de sortie, erreurs, trous de données et limites :
- Rendement total / annualisé :
- Drawdown maximal, date et durée :
- Volatilité, Sharpe/Sortino et conventions, dont taux sans risque :
- Rendement et risque de la référence ; écart de rendement :
- Rotation et définition utilisée, ordres, exécutions et coûts :
- Exposition, concentration par titre/secteur et séances sans position :
- Cash minimal, durée du cash négatif et financement implicite :
- Rejets, annulations, ordres en attente, exécutions partielles et rapprochement des positions :
- Cycles exécutés/manqués/échoués et décisions sans ordre :
- Coût et erreurs IA, le cas échéant :
- Rapports natifs, logs, configuration figée et empreintes des données :
- Rejeu : identifiant de l’exécution distincte et différences constatées :
- Verdict sur la validité technique du test :
- Verdict sur l’hypothèse et respect des critères définis :
- Décision et prochaine expérience proposée :

**Règle :** écrire « non mesuré » ou « indisponible » plutôt que remplir une donnée inconnue. Tout résultat invalide reste au journal avec son motif.

## 7. Références historiques — hors registre des nouveaux tests actions

Ces chiffres sont repris des documents existants ; ils n’ont pas été recalculés lors de la création du journal.

| Référence | Univers | Période | Conditions | Yahoo | Alpaca |
|---|---|---|---|---:|---:|
| Étape 2 Momentum original | ETF SPY/VEU/AGG | 2021–2025 | 100 000 USD, guard désactivé ; deux exécutions par source | +19,53 % | +18,84 % |
| Rejeu rapide Momentum | Mêmes ETF | 2021–2025 | Mode sans emprunt ; une exécution par source, nombreux refus mal gérés | −2,83 % | −2,72 % |

Réserves : cash parfois négatif sans intérêts modélisés dans la référence non protégée ; dividendes non crédités au portefeuille ; différences de données et de prix. Le rejeu actif ne mesure pas isolément le coût du financement.

Ces références ne valident ni les actions S&P 500, ni les quatre moments, ni une stratégie candidate. Les preuves détaillées doivent être retrouvées avant d’attribuer un chemin de rapport ; elles ne sont pas supposées présentes dans ce dossier.

## 8. Prochaine étape

Préparer le protocole de STR-01, en commençant par la faisabilité de l’univers et des données historiques. Ne fixer ni fenêtre de momentum, ni nombre de positions, ni période finale sans décision explicite. Le socle actuel suffit pour poursuivre la recherche ; compléter l’architecture seulement quand un besoin du test le justifie.
