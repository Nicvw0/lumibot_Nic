# Mini-fonds d’actions S&P 500 — Plan de développement local

Plan de référence et décisions validées pour les recherches en backtesting.

**Dernière mise à jour :** 30 octobre 2026  
**Statut :** étape 2 terminée avec réserves ; phase B à préparer  
**Public :** propriétaire du projet et agents chargés des recherches

## 1. Objectif du projet

Construire progressivement un mini-fonds d’investissement **en actions individuelles appartenant au S&P 500**, sur le marché américain, d’abord en **backtesting**, puis en **Alpaca Paper Trading** après qualification. Le projet fonctionne localement sous Windows, avec LumiBot comme moteur. SPY peut servir de benchmark ou d’indicateur ; les ETF ne constituent pas le portefeuille cible de cette première version.

Le système devra, à terme :

1.  Analyser le marché avant l'ouverture de la Bourse américaine.
2.  Évaluer les actions suivies, les positions existantes et les
    opportunités éventuelles.
3.  Décider de manière contrôlée s'il faut acheter, vendre ou conserver.
4.  Réévaluer la situation lors de **quatre activations par séance normale** : avant ouverture, après ouverture, en cours de séance et avant clôture. Les heures précises restent à fixer ; chaque cycle peut conclure à aucune transaction.
5.  Enregistrer les analyses, décisions, ordres, erreurs et résultats.
6.  Permettre de suivre le portefeuille et les tests depuis une
    interface web locale simple.

L'IA ne doit pas pouvoir contourner les limites de risque. Elle peut
analyser et proposer des décisions, mais des règles déterministes en
Python doivent valider les ordres avant leur envoi à Alpaca.

## 2. Point de départ technique

-   **Dépôt de base :** https://github.com/Lumiwealth/lumibot
-   **Installation actuelle :** dépôt cloné sur le PC et dépendances de
    `requirements.txt` installées.
-   **Environnement initial :** localhost, sans hébergement distant.
-   **Broker prévu pour les essais :** Alpaca Paper Trading.
-   **Approche :** privilégier le backtesting reproductible et les
    petites étapes validées plutôt que construire tout le système d'un
    seul coup.
-   **Pas de trading réel dans cette première version.**

**Référence d’audit historique :** LumiBot `4.6.33`, commit `a5f0ee6d` (`dev`), Python `3.13.5`, Windows 11, audit initial Antigravity. Depuis, les backtests et les exemples ont été réexaminés dans la conversation ; un garde-fou de financement a été installé par l’utilisateur. Le commit d’audit n’est pas présenté comme le dernier commit de l’état local actuel.

## 3. Inspirations pour l'interface et l'architecture

### A. LumiBot --- moteur principal

Dépôt : https://github.com/Lumiwealth/lumibot

LumiBot reste la base du système : stratégies, backtesting et connexion
au broker. L'interface ne doit pas réimplémenter ces fonctions. Elle
doit afficher les informations produites par le moteur et déclencher
uniquement des opérations explicitement autorisées par le backend.

Documentation de déploiement :
https://lumibot.lumiwealth.com/deployment.html

### B. BotSpot --- référence de produit et d'expérience utilisateur

Site : https://botspot.trade/

BotSpot est une plateforme liée à l'écosystème LumiBot, et non un dépôt
GitHub équivalent au projet LumiBot. Elle sert de référence pour
réfléchir aux fonctions d'une interface de trading : gestion des
stratégies, suivi des exécutions, visualisation des résultats et accès
aux journaux.

Il ne faut pas présumer que toutes ses fonctions sont gratuites,
ouvertes ou réutilisables. L'objectif est de s'inspirer des besoins
couverts, pas de copier son code ou de dépendre de son service.

### C. AI Stock Trading Bot --- référence open source d'interface

Dépôt : https://github.com/Anjoliekate/AI-Stock-Trading-Bot

Ce projet est une piste d'inspiration pour une architecture web séparant
une interface Vue.js, un backend Flask et des données de suivi. Son état
actuel, ses dépendances, son fonctionnement et sa compatibilité avec la
version locale de LumiBot doivent être vérifiés avant de réutiliser un
élément.

L'objectif n'est pas de fusionner les dépôts ni de remplacer LumiBot.
Antigravity peut examiner ce projet pour identifier des idées
d'interface et de séparation frontend/backend, puis ne reprendre que les
concepts utiles et compatibles.

## 4. Principe d'architecture recommandé

Au départ, garder une architecture locale simple :

-   **LumiBot / stratégies Python :** backtests et logique de trading.
-   **Backend local :** API Python qui expose des données de suivi et
    des commandes autorisées à l'interface.
-   **Interface web locale :** tableau de bord lisible dans un
    navigateur.
-   **Stockage local :** SQLite au départ, si une base persistante est
    nécessaire, pour conserver les exécutions, décisions, configurations
    et résultats.
-   **Alpaca Paper Trading :** utilisé uniquement lors de la phase paper
    trading.
-   **Clés API :** conservées côté serveur dans un fichier
    d'environnement ignoré par Git ; jamais exposées au navigateur ni
    inscrites dans le code source.

Le frontend ne doit jamais appeler directement Alpaca avec des clés
secrètes. Il ne doit pas exécuter lui-même les stratégies ou calculs
financiers critiques.

### Règle centrale : validation indépendante des propositions des IQ

Les IQ (agents d'intelligence artificielle) peuvent analyser les données
et proposer une action — acheter, vendre, conserver ou ne rien faire —
mais elles ne doivent **jamais envoyer elles-mêmes un ordre au broker**.
Chaque proposition doit passer par une couche de validation déterministe
en Python, intégrée au backend et utilisant LumiBot ainsi que les données
de marché et de portefeuille vérifiées.

Cette couche doit, selon les règles définies et testées pour la stratégie :

1. Vérifier que les données sont disponibles, suffisamment récentes et
   cohérentes ; en cas de doute, bloquer l'ordre.
2. Confronter la proposition aux signaux mesurables de la stratégie
   (par exemple tendance, momentum, conditions d'entrée/sortie et
   indicateurs retenus). Le code peut confirmer ou infirmer la thèse de
   l'IQ ; il ne doit pas simplement approuver automatiquement son avis.
3. Vérifier l'état réel du portefeuille, les liquidités, les positions et
   les ordres déjà ouverts ou en cours afin d'éviter les incohérences et
   doublons.
4. Appliquer des limites indépendantes de l'IA : taille maximale d'ordre,
   exposition par action et globale, budget disponible et autres règles
   de risque définies pour le projet.
5. Produire un résultat explicite : `APPROVED`, `REJECTED` ou
   `REVIEW_REQUIRED`, accompagné d'une raison structurée. Seul un ordre
   `APPROVED` peut être transmis à LumiBot/broker, et uniquement si tous
   les contrôles de sécurité obligatoires passent.

Si la proposition de l'IQ contredit les règles de stratégie, si les données
sont périmées, si un contrôle échoue ou si un état important est inconnu,
la règle par défaut est **aucun nouvel ordre**. Une IQ ne peut jamais
modifier ses propres limites de risque ni contourner un rejet Python.

Le journal doit conserver séparément : la proposition originale de l'IQ,
les données et signaux utilisés pour la vérification, le résultat de chaque
contrôle, la décision finale Python, la raison d'une confirmation ou d'un
rejet, puis le statut de l'ordre retourné par le broker. Ainsi, une
recommandation de l'IQ n'est pas confondue avec une décision validée ou
avec un ordre effectivement exécuté.

Cette validation permet de tester la cohérence d'une proposition avec des
critères objectifs ; elle ne garantit pas que l'analyse soit correcte ni
que l'opération soit profitable. Les règles doivent être testées en
backtest et en paper trading avant toute automatisation.

### Stack possible, à confirmer après inspection

-   Backend : Python avec Flask ou FastAPI. Choisir une seule option, de
    préférence celle qui s'intègre le plus simplement au code existant.
-   Frontend : HTML/CSS/JavaScript simple pour la première version, ou
    Vue si le dépôt de référence apporte un avantage clair.
-   Stockage : fichiers de résultats existants et/ou SQLite.
-   Graphiques : une bibliothèque légère seulement si nécessaire.

**Règle :** ne pas ajouter une stack complexe, Docker, Kubernetes,
MongoDB ou une architecture multi-agents avant qu'un besoin concret ne
le justifie.

## 5. Interface minimale --- première version

L'objectif initial est une interface fonctionnelle et sobre, pas un
terminal professionnel complet.

### Écran 1 --- Vue d'ensemble

Afficher, quand les données sont disponibles :

-   mode actuel : backtest ou paper trading ;
-   capital de départ et valeur du portefeuille ;
-   liquidités disponibles ;
-   rendement global et rendement sur la période sélectionnée ;
-   drawdown maximal ;
-   positions ouvertes ;
-   dernière mise à jour et statut du système.

Ne pas inventer de données si aucune exécution n'a encore eu lieu :
afficher un état vide clair.

### Écran 2 --- Positions

Pour chaque position :

-   symbole de l'action ;
-   quantité ;
-   prix d'entrée moyen ;
-   prix actuel, si disponible ;
-   valeur de la position ;
-   gain/perte non réalisé, en valeur et en pourcentage.

Afficher l'heure de mise à jour des données et signaler les données
manquantes ou périmées.

### Écran 3 --- Stratégies et backtests

-   liste des stratégies disponibles ;
-   période et paramètres utilisés ;
-   rendement, drawdown, nombre de transactions et benchmark ;
-   accès aux résultats détaillés ;
-   comparaison de plusieurs exécutions.

Au début, lancer les backtests depuis la ligne de commande peut suffire.
L'interface peut d'abord afficher les résultats enregistrés. Le
lancement d'un backtest depuis le navigateur pourra être ajouté ensuite,
avec contrôle des erreurs et des tâches longues.

### Écran 4 --- Journal des analyses et décisions

Pour chaque cycle :

-   date et heure ;
-   stratégie ou agent à l'origine de l'analyse ;
-   actions analysées ;
-   recommandation : acheter, vendre, conserver ou ne rien faire ;
-   justification résumée ;
-   validation ou rejet par les règles de risque ;
-   ordre envoyé ou absence d'ordre ;
-   résultat et erreurs éventuelles.

Distinguer clairement une **suggestion de l'IA**, une **décision
autorisée par les règles**, et un **ordre réellement accepté par le
broker**.

### Écran 5 --- Contrôles de sécurité

Prévoir progressivement :

-   mode lecture seule ;
-   activation/désactivation des analyses planifiées ;
-   arrêt d'urgence empêchant de nouveaux ordres ;
-   limites de taille d'ordre et d'exposition ;
-   confirmation explicite avant tout changement important de
    configuration.

L'arrêt d'urgence doit être appliqué côté backend et ne pas dépendre
uniquement de l'interface.

## 6. Feuille de route actualisée — une étape validée à la fois

**État actuel :** les étapes initiales de validation du moteur sont terminées. L’étape 2 de la conversation inclut une référence Momentum originale sur ETF, complète et reproductible sur Yahoo et Alpaca, avec réserves. La phase B est réorientée vers les actions du S&P 500 ; aucun résultat antérieur sur ETF ne valide cette future stratégie. Le détail des acquis et des réserves suit la phase A historique.

**Règle de travail :** partir des exemples existants, conserver les originaux intacts, réaliser une seule modification logique par étape, produire un livrable vérifiable et attendre validation avant la suite. Les réglages ci-dessous sont des **hypothèses à tester**, pas des paramètres optimaux.

### Phase A — Rendre les backtests reproductibles (historique terminé)

- [x] **Étape 0 — Auditer le dépôt.** Rapport disponible localement : `docs/audit_strategies_lumibot.md`. Version auditée : LumiBot 4.6.33, commit `a5f0ee6d`.
- [x] **Étape 1 — Corriger la configuration des tests sans toucher au moteur.** Sous PowerShell, utiliser `$env:PYTHONUTF8 = "1"` et `$env:PYTHONIOENCODING = "utf-8"`. Examiner les valeurs factices de `DATADOWNLOADER_BASE_URL` et `BACKTESTING_DATA_SOURCE` dans `.env` ; sauvegarder les réglages utiles, neutraliser les placeholders bloquants sans divulguer les secrets, sélectionner explicitement une source historique fonctionnelle. Diagnostiquer les délais d’attente plutôt que laisser des processus bloqués.
  - **Validation :** source de données identifiée, historique effectivement accessible, configuration documentée, aucune clé exposée.
- [x] **Étape 2 — Exécuter un backtest LumiBot inchangé.** Utiliser un exemple simple tel que `lumibot/example_strategies/stock_buy_and_hold.py`. Enregistrer commande, période, univers, source de données, commit, frais, sorties et éventuelles erreurs. Relancer le même test.
  - **Validation :** deux exécutions abouties et reproductibles, avec un rapport de performance exploitable et une comparaison de référence pertinente (SPY lorsque disponible).

### Complément à la phase A — Référence Momentum terminée

L'étape 2 de la conversation est **terminée avec réserves** : Momentum original sur SPY/VEU/AGG, 100 000 USD, période 2021–2025, deux exécutions reproductibles par source. Rendements sans garde-fou : **+19,53 % Yahoo / +18,84 % Alpaca**. Ces ETF constituent un test historique du moteur et de l'exemple ; ce n'est pas la validation du futur mini-fonds d'actions du S&P 500.

Les réserves portent sur les liquidités parfois négatives sans financement facturé, les dividendes non crédités au portefeuille et les conventions de prix différentes. Un contrôle de financement à trois modes est désormais installé et testé pour les ordres simples actions/ETF en backtest. Un rejeu rapide en mode sans emprunt a donné **−2,83 % Yahoo / −2,72 % Alpaca**, sans cash négatif, mais avec de nombreux refus que Momentum ne gère pas correctement. Ces résultats ne mesurent donc pas seulement la suppression de l'emprunt.

**Décision de travail : garde-fou désactivé pendant les backtests exploratoires.** Le mode et les déficits de cash restent visibles dans les résultats. La protection sera réévaluée lorsqu'une stratégie pertinente aura été identifiée, avec un dimensionnement et une gestion des refus cohérents. Le contrôle de financement existant ne constitue pas à lui seul le futur Risk Gate complet ni une protection Paper/Live.

### Phase B — Mise au point sur actions individuelles du S&P 500, avec quatre cycles quotidiens

Cette phase remplace l'ancien programme « Top N ETF ». Les étapes ci-dessous sont à réaliser ; elles ne sont pas déclarées validées par les tests antérieurs sur ETF.

- [ ] **Étape 3 — Définir l'univers S&P 500 et le protocole des quatre activations.** Utiliser uniquement des actions individuelles appartenant à l'indice à la date simulée. Définir des critères de liquidité, d'historique et de qualité des données ; ne pas sélectionner rétrospectivement les gagnants actuels. Le S&P 500 entier est le réservoir autorisé ; un sous-univers de prototype reste une option à définir, pas une décision d'acheter ou de suivre obligatoirement un nombre fixe de titres.
  - Les quatre cycles sont : **avant ouverture**, **après ouverture**, **en cours de séance**, **avant clôture**. Ils peuvent analyser, confirmer, gérer ou ne rien faire. Les heures précises, les règles des séances écourtées et le traitement des jours sans marché restent à fixer avant le test.
  - Utiliser le fuseau **America/New_York** et le calendrier de marché ; quatre cycles d'une séance normale ne signifient ni quatre achats ni quatre rééquilibrages obligatoires. Une position peut être conservée plusieurs jours.
  - **Point technique vérifié :** dans cette installation, `Strategy.register_cron_callback` ne fait rien en mode backtest. `schedule_function.py` est un exemple de planification Paper/Live, pas la preuve d'un ordonnancement historique. Les quatre cycles doivent être reproduits à partir de l'horloge simulée et de barres adaptées, avec un journal prouvant qu'ils ont eu lieu une seule fois chacun.
  - Des données journalières suffisent pour étudier un classement quotidien, mais ne valident pas quatre prix d'exécution intrajournaliers distincts. Vérifier la couverture intraday et les droits du flux avant de tester les quatre activations. Ne pas créer artificiellement quatre barres à partir d'une barre journalière.
  - **Validation :** univers et paramètres définis avant calcul, qualité des données contrôlée, calendrier documenté, quatre cycles observables et aucune donnée future dans les décisions.

- [ ] **Étape 4 — Établir la référence Momentum sur actions du S&P 500.** Réutiliser la logique de `stock_momentum.py` dans une variante distincte, sans modifier l'exemple d'origine. Définir une sélection de plusieurs actions, ses poids, ses limites sectorielles et sa cadence de rééquilibrage. Le réglage de deux jours de l'exemple n'est pas un paramètre déjà validé pour ce nouveau portefeuille.
  - Tester des horizons et un nombre de positions fixés à l'avance ; les horizons de plusieurs semaines ou mois sont des hypothèses, pas une optimisation acquise. Les suggestions antérieures 60/90/120 jours ou Top 1/3/5 ne sont pas des décisions du projet.
  - Conserver le garde-fou désactivé selon la décision exploratoire actuelle. Enregistrer la trésorerie minimale, l'exposition et toute utilisation implicite de marge. Rapprocher les variables de stratégie avec les positions et ordres réellement simulés.
  - **Validation :** deux exécutions complètes reproductibles, transactions explicables, portefeuille effectivement constitué d'actions autorisées, comparaison à une référence S&P 500/SPY clairement documentée. SPY reste un benchmark ou un indicateur ; il n'est pas une position du mini-fonds.

- [ ] **Étape 5 — Tester le suivi de tendance séparément.** Examiner `ai_researcher_trader.py` (exemple IA sur un symbole, moyenne de 20 barres) et les composants `SMAIndicator` disponibles. Définir une règle vérifiable sur les actions et/ou un filtre de régime du marché. Une moyenne de 20 barres ou de 200 jours est un candidat de test, pas un réglage imposé.
  - Distinguer le suivi de tendance d'un titre et le filtre de marché appliqué au portefeuille. Comparer d'abord une version sans filtre et une version avec filtre ; ne pas attribuer à une étude du facteur momentum la validation de notre code précis.
  - **Validation :** règles, signaux et invalidations explicites ; comparaison sur les mêmes périodes, univers et hypothèses de coûts, avec les quatre cycles journalisés.

- [ ] **Étape 6 — Comparer Momentum, tendance et leur combinaison.** Conserver des variantes séparées : Momentum seul, tendance seule lorsque pertinente, Momentum avec filtre. Ne pas ajouter simultanément plusieurs horizons, indicateurs, agents et pondérations.
  - Comparer rendement, drawdown, volatilité, rotation, exposition, concentration, coûts et trésorerie. Les quatre activations constituent un protocole d'observation/action, pas une obligation de rendre les signaux artificiellement plus fréquents.
  - **Validation :** effet de chaque modification isolé, critères d'acceptation définis avant examen du résultat, expérience archivée et décision explicite de poursuivre ou d'abandonner chaque variante.

### Phase C — Robustesse, sélection d'une candidate et exécution cohérente

- [ ] **Étape 7 — Tester la robustesse et sélectionner une candidate.** Comparer différentes conditions de marché et une sensibilité raisonnable aux paramètres. Séparer conception, validation et test final réellement réservé. **2021–2025 a déjà été consultée et reste exploratoire** ; la découper aujourd'hui ne suffit pas à en faire un test final jamais vu.
  - Utiliser les membres historiques du S&P 500, les dates effectives d'entrée/sortie et des identifiants évitant les confusions de tickers. Documenter les données indisponibles plutôt que les remplacer. Traiter explicitement dividendes, splits, prix d'exécution et valorisation.
  - **Validation :** résultats reproductibles, nets des hypothèses de coûts documentées, comparaison à la référence et limites connues. Aucun rendement isolé ne suffit à sélectionner la stratégie.

- [ ] **Étape 8 — Fiabiliser les ordres et préparer le Risk Gate indépendant.** Une fois une candidate pertinente trouvée, adapter son dimensionnement, l'attente des ventes et sa gestion des ordres partiels/refusés. Les positions doivent découler des exécutions confirmées, pas des tentatives de soumission.
  - Refaire alors les tests avec le garde-fou activé : `cash` sans emprunt ou `margin` avec plafond explicite ; comparer proprement au mode `disabled`. Le contrôle installé couvre les ordres simples long-only actions/ETF en backtest, pas les brackets, dérivés, comptes partagés réels ou tous les événements de trésorerie.
  - Construire ensuite le Risk Gate Python complet : fraîcheur des données, appartenance à l'univers, positions/ordres ouverts, doublons, exposition, limites par ligne et secteur, politique de marge, arrêt d'urgence et mode d'exécution. Les seuils restent à décider ; ils ne sont pas fixés par ce plan.
  - Pour les IQ : `APPROVED`, `REJECTED` ou `REVIEW_REQUIRED`, avec motifs. La désactivation exploratoire du garde-fou cash n'autorise pas un contournement des contrôles lors d'un futur passage Paper/Live.
  - **Validation :** refus et exécutions partielles correctement traités, absence de doublons, risque autorisé respecté, journal proposition → contrôles → décision → ordre → résultat broker. Aucun ordre Paper/Live dans cette phase.

### Phase D — Historisation, interface et Alpaca Paper Trading

- [ ] **Étape 9 — Historiser les expériences et les quatre cycles.** Réutiliser les statistiques et journaux LumiBot. Enregistrer période, univers historique, code, données, coûts, mode de garde-fou, événements de cash et décisions de chaque activation. Ajouter SQLite seulement si nécessaire.
- [ ] **Étape 10 — Construire une interface locale en lecture seule.** Afficher les résultats, positions confirmées, ordres ouverts/refusés, risques, état des quatre cycles et erreurs. Ne pas inventer de positions ou de performances en absence de données.
- [ ] **Étape 11 — Préparer Alpaca Paper Trading.** Vérifier explicitement le compte Paper et les fonctions réellement disponibles du broker. Distinguer cash, fonds réglés et pouvoir d'achat. Qualifier séparément les contrôles d'ordres connectés : le garde-fou de backtest ne prouve pas une protection Paper/Live. Tester reprise, rejets, annulations, ordres partiels et arrêt d'urgence.
- [ ] **Étape 12 — Observer une seule stratégie candidate en Paper.** Utiliser l'univers d'actions S&P 500 et les quatre cycles validés. Documenter les écarts entre simulations et exécutions Paper. Ne pas étendre tant que les incidents et différences ne sont pas compris. Aucun trading réel sans nouvelle décision explicite.

### Phase E — Stratégies complémentaires et recherches ultérieures

Ces pistes ne deviennent pas automatiquement des fonctionnalités à implémenter. Elles seront évaluées séparément, avec leur propre protocole de données et de coûts.

- [ ] **Étape 13 — Breakout d'ouverture, si une activité intraday est retenue.** `ai_opening_range_breakout.py` est un exemple **IA**, range de quinze minutes et cadence horaire ; il ne constitue pas une stratégie Python déterministe déjà validée sur toutes les actions S&P 500. Adapter l'univers, définir les entrées et sorties et vérifier la surveillance/protection entre les quatre cycles. Une étude sur un ORB de cinq minutes et un univers américain plus large ne valide pas cet exemple précis.
- [ ] **Étape 14 — Retour à la moyenne, comme stratégie distincte.** L'exemple déterministe `ccxt_backtesting_example.py` utilise la crypto ; ses bandes de Bollinger doivent être adaptées et testées sur actions. `RSIIndicator`, `BollingerBandsIndicator` et `VWAPIndicator` sont des composants, pas des preuves de rendement. `ai_vwap.py` est un autre exemple IA, sur SPY par défaut ; il n'est pas un portefeuille d'actions S&P 500 prêt à l'emploi.
- [ ] **Étape 15 — Qualité/valorisation, avec un horizon adapté.** Examiner `ai_trading_team_warren_buffett_value.py` et `ai_trading_team_bill_ackman_concentrated.py`. Ce sont des exemples à agents et à univers restreints, pas des implémentations validées de facteurs académiques. Les quatre cycles peuvent suivre les annonces sans imposer quatre changements de sélection fondamentale par jour. Respecter les dates de publication réelles des données.
- [ ] **Étape 16 — Ajouter l'IA comme recherche et mise en contradiction.** Examiner `ai_trading_team_bull_bear_large_cap_stocks.py` et `ai_researcher_trader.py` pour leur organisation recherche → critique → décision. Les exemples ont parfois un agent autorisé à trader ; ils ne sont pas à copier tels quels dans notre architecture où la décision finale et l'autorisation d'ordre sont vérifiées par Python. Mesurer la valeur ajoutée et le coût de l'IA séparément du signal de prix. Les exemples Citadel/rotation d'ETF ne respectent pas notre univers s'ils sont repris sans adaptation.
- [ ] **Étape 17 — Évaluer l'hébergement après fiabilité locale et Paper.** Prérequis : suivi des quatre cycles, reprise après panne, secrets protégés et observations Paper documentées.

**Distinctions à conserver :** stratégie de sélection, filtre de marché, rééquilibrage, garde-fou, planification et architecture d'agents sont des fonctions différentes. Leur présence dans LumiBot ne démontre pas un avantage de trading.

## 7. Règles de sécurité et de qualité

- Les recherches actuelles restent en backtesting ; aucun nouvel ordre Paper/Live n'est autorisé par ce document.
- Univers négocié : actions individuelles du S&P 500, avec appartenance historique pour les simulations. Pas de panier d'ETF, d'options, de crypto ou de marché canadien dans cette première version. SPY peut servir de benchmark ou d'indicateur.
- Quatre activations par séance normale : analyse et/ou action, avec `HOLD` ou absence d'ordre comme résultat valide. Les heures exactes restent à valider. Utiliser des barres réellement connues au moment de chaque cycle.
- Garde-fou cash **désactivé pour l'exploration actuelle** ; enregistrer ce mode, les déficits de cash et les coûts de financement omis. Réévaluer les modes actifs sur une candidate avant tout passage opérationnel.
- Conserver les limites de risque et la validation finale dans le backend Python, indépendantes des IQ. Une proposition d'IQ n'est ni une autorisation ni une exécution.
- Ne pas confondre ordre soumis, accepté, partiel, refusé, annulé et exécuté. Rapprocher les positions avec les événements broker ; prévenir les doublons et tenir compte des ordres ouverts.
- Ne jamais exposer les secrets dans Git, le navigateur ou les journaux ; ne pas publier de données privées du compte dans ces documents.
- Documenter les sources, les dates de disponibilité, les coûts, les ajustements et les limites des historiques. Ne pas inventer de données manquantes.
- Préserver les exemples d'origine ; faire une modification logique par expérience, conserver les essais et éviter les réglages a posteriori sur une seule période.
- Les commits et envois vers GitHub sont effectués par l'utilisateur. Ce plan n'autorise ni commit, ni push, ni release ou déploiement automatique.

## 8. Priorité immédiate et documents de référence

**Prochaine étape : étape 3 de la phase B.** Définir le protocole d'univers S&P 500 et des quatre cycles simulés avant de développer les variantes de sélection. Les étapes 0–2 ne sont pas à recommencer comme si elles étaient bloquées.

Ordre de mise au point : univers/horaire/données → Momentum actions → tendance → comparaisons → robustesse/candidate → exécution et contrôles complets → interface → Paper. Breakout intraday, retour à la moyenne, qualité fondamentale et agents spécialisés restent des pistes séparées.

Documents du même dossier :

- [Stratégies, état réel des exemples et protocole](strategies_trading_mini_fonds_lumibot.md).
- [Synthèse de l'audit et décisions en vigueur](synthese_audit_strategies_lumibot.md).
- [Audit historique détaillé](../docs/audit_strategies_lumibot.md) : état d'origine, à lire avec les mises à jour ci-dessus.
- [Garde-fou cash installé : périmètre technique](../docs/CASH_GUARD.md).

Les rapports détaillés produits dans la conversation (`rapport_final_etape_2.md`, `rapport_comparatif.md`) conservent les preuves des tests sur ETF et des essais avec protection. Ils ne sont pas présentés comme des fichiers déjà rapatriés dans ce dépôt.

## 9. Prochain mandat de travail

> Préparer uniquement l'étape 3 de la phase B. Partir des décisions validées : actions individuelles du S&P 500, quatre activations par séance normale, backtesting avant Paper et garde-fou cash désactivé pour l'exploration. Proposer un univers historique documenté, vérifier les historiques disponibles et définir les rôles des quatre cycles avant de fixer leurs heures. Vérifier la capacité du moteur à reproduire ces cycles dans son horloge simulée : `register_cron_callback` est ignoré en backtest dans cette installation. Ne pas fabriquer de barres intraday à partir de données journalières. Distinguer les décisions déjà prises des paramètres restant à arbitrer ; ne pas présenter les exemples IA comme des algorithmes déterministes validés. Conserver les stratégies d'origine et ne pas modifier de code, lancer d'agent facturé, passer d'ordre ou commencer une autre étape sans mandat explicite. Fournir un protocole vérifiable puis attendre la décision de l'utilisateur.

**Principe directeur :** rechercher un avantage vérifiable sur actions S&P 500, respecter quatre cycles de décision sans imposer quatre transactions, mesurer les coûts et limites, et conserver une validation Python indépendante des propositions d'IA.
