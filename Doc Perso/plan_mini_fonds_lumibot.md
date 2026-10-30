# Mini-fonds avec LumiBot — Plan de développement local (actualisé après audit)

## 1. Objectif du projet

Construire progressivement un mini-fonds d'investissement **en ETF dans la première phase (actions et autres classes d’actifs représentées par des ETF), puis éventuellement en actions individuelles**, d'abord en **backtesting**, puis en **paper trading avec
un compte Alpaca gratuit**. Le projet doit fonctionner localement sur le
PC Windows de son propriétaire, avec LumiBot comme moteur de trading.

Le système devra, à terme :

1.  Analyser le marché avant l'ouverture de la Bourse américaine.
2.  Évaluer les actions suivies, les positions existantes et les
    opportunités éventuelles.
3.  Décider de manière contrôlée s'il faut acheter, vendre ou conserver.
4.  Réévaluer la situation à quatre moments définis de la journée.
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

**Audit déjà effectué par Antigravity** : LumiBot `4.6.33`, commit `a5f0ee6d` (`dev`), Python `3.13.5`, Windows 11. Les chemins et résultats ci-dessous sont issus du rapport de l’agent, non d’une seconde vérification indépendante. Réinspecter après toute mise à jour du dépôt.

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

**État de départ (rapport Antigravity) :** audit du dépôt terminé ; 43 tests unitaires réussis ; compte Alpaca **Paper** déclaré actif et consultation du cours de SPY réussie. **Aucun backtest complet validé** : plusieurs essais ont été interrompus ou bloqués. Aucun résultat de performance de stratégie n’est donc acquis.

**Règle de travail :** partir des exemples existants, conserver les originaux intacts, réaliser une seule modification logique par étape, produire un livrable vérifiable et attendre validation avant la suite. Les réglages ci-dessous sont des **hypothèses à tester**, pas des paramètres optimaux.

### Phase A — Rendre les backtests reproductibles (priorité immédiate)

- [x] **Étape 0 — Auditer le dépôt.** Rapport disponible localement : `docs/audit_strategies_lumibot.md`. Version auditée : LumiBot 4.6.33, commit `a5f0ee6d`.
- [x] **Étape 1 — Corriger la configuration des tests sans toucher au moteur.** Sous PowerShell, utiliser `$env:PYTHONUTF8 = "1"` et `$env:PYTHONIOENCODING = "utf-8"`. Examiner les valeurs factices de `DATADOWNLOADER_BASE_URL` et `BACKTESTING_DATA_SOURCE` dans `.env` ; sauvegarder les réglages utiles, neutraliser les placeholders bloquants sans divulguer les secrets, sélectionner explicitement une source historique fonctionnelle. Diagnostiquer les délais d’attente plutôt que laisser des processus bloqués.
  - **Validation :** source de données identifiée, historique effectivement accessible, configuration documentée, aucune clé exposée.
- [x] **Étape 2 — Exécuter un backtest LumiBot inchangé.** Utiliser un exemple simple tel que `lumibot/example_strategies/stock_buy_and_hold.py`. Enregistrer commande, période, univers, source de données, commit, frais, sorties et éventuelles erreurs. Relancer le même test.
  - **Validation :** deux exécutions abouties et reproductibles, avec un rapport de performance exploitable et une comparaison de référence pertinente (SPY lorsque disponible).

### Phase B — Première stratégie : Momentum existant, puis adaptations

- [ ] **Étape 3 — Tester le Momentum original.** Partir de `lumibot/example_strategies/stock_momentum.py` et de `Bars.get_momentum()`. Ne pas modifier le fichier source d’origine ; créer une variante seulement si nécessaire. Documenter la concentration de l’exemple sur un actif et ses règles réelles d’entrée/sortie.
  - **Validation :** backtest complet, métriques, transactions, limites de données, benchmark SPY et période hors échantillon réservée.
- [ ] **Étape 4 — Adapter le Momentum à un panier d’ETF.** Univers candidat : `SPY`, `QQQ`, `IWM`, `GLD`, `TLT`, `VNQ`, `SHV` (vérifier disponibilité, historique, liquidité et corrélations). Comparer fenêtres **60/90/120 jours**, puis **Top 1/3/5**, sans optimiser simultanément tous les réglages. Les ETF ne sont pas tous indépendants ; vérifier aussi la concentration effective.
  - **Validation :** mêmes périodes, hypothèses de coûts/slippage explicites, résultats comparables, absence de biais de regard vers le futur ; cohérence des poids (Top 1 incompatible avec un plafond de 30 % si l’on veut être entièrement investi).
- [ ] **Étape 5 — Réutiliser le rééquilibrage existant.** Étudier `lumibot/example_strategies/drift_rebalancer.py` et `DriftRebalancerLogic`, sans supposer leur compatibilité directe avec le Momentum. Tester la vente avant l’achat, les poids cibles, le cash et les ordres partiels. Comparer différentes fréquences de rééquilibrage.
  - **Validation :** positions et ordres simulés cohérents, pas de doublons, cash non négatif, coûts intégrés.
- [ ] **Étape 6 — Ajouter le filtre de tendance.** Utiliser les composants SMA existants (`lumibot/indicators/builtin.py`) pour tester **SPY au-dessus/en dessous de sa SMA 200 jours**. Comparer Momentum seul et Momentum + filtre ; lorsque le filtre est négatif, tester séparément cash et `SHV` (qui n’est pas équivalent au cash).
  - **Validation :** comparaison robuste hors échantillon, sans conclure sur un seul rendement favorable.

### Phase C — Sécurité indépendante et sélection de la version candidate

- [ ] **Étape 7 — Implémenter le Risk Gate Python déterministe.** La méthode native `_validate_order` a été jugée insuffisante dans l’audit. Contrôler avant toute soumission : données fraîches, liquidités réellement disponibles, positions et ordres ouverts, doublons, exposition globale/par ligne, levier **≤ 1** pour la première version, limites de taille, kill switch et environnement **Paper uniquement**. Plafond par ligne (par exemple 30 %) et tampon cash (par exemple 10 %) sont des **paramètres initiaux à arbitrer**, non des règles définitivement validées. Renvoyer `APPROVED`, `REJECTED` ou `REVIEW_REQUIRED` ; les deux derniers interdisent l’envoi d’un ordre.
  - **Validation :** tests automatisés des cas de refus, échecs sûrs en cas d’incertitude, journal proposition → validation → ordre → réponse broker ; aucun chemin de contournement par l’IA ou l’interface.
- [ ] **Étape 8 — Comparer et figer une version candidate.** Tableau commun : CAGR/rendement annualisé, drawdown max, volatilité, Sharpe/Sortino si pertinents, turnover, exposition, nombre de transactions, coûts, robustesse selon les régimes et test final hors échantillon. Comparer à SPY buy-and-hold et à la version Momentum initiale.
  - **Validation :** règles et paramètres versionnés, justification du choix documentée, aucun ajustement après consultation du jeu final sans nouveau découpage des données.

### Phase D — Application locale et paper trading

- [ ] **Étape 9 — Historiser les résultats.** Réutiliser d’abord les journaux et rapports LumiBot ; ajouter SQLite seulement si nécessaire. Identifier chaque exécution (commit, paramètres, données, dates, frais, décisions, ordres).
- [ ] **Étape 10 — Backend et interface locale en lecture seule.** API affichant état, résultats, positions, journal, erreurs et risques ; construire les écrans prévus en section 5. Aucun bouton d’envoi d’ordre à ce stade.
- [ ] **Étape 11 — Préparer Alpaca Paper Trading.** Vérifier explicitement l’URL et les clés **Paper**, distinguer cash de pouvoir d’achat (le rapport signale 10 000 $ de cash et 40 000 $ de buying power : ne pas interpréter cela comme une autorisation de levier). Tester connexion, lecture des positions, simulation/dry-run, rejets, ordres partiels, reprise et kill switch.
- [ ] **Étape 12 — Observer une seule stratégie en paper trading.** Démarrer avec la version Momentum retenue, taille prudente, journaux quotidiens et rapprochement décisions/ordres/positions. Ne pas étendre tant que les incidents et écarts ne sont pas compris.
  - **Validation :** période d’observation documentée, pas de contournement du Risk Gate, fonctionnement stable et écarts de simulation expliqués.

### Phase E — Autres stratégies et fonctions avancées (après la référence Momentum)

- [ ] **Étape 13 — Tester Breakout séparément.** Examiner `ai_opening_range_breakout.py` et `donchian_midline.py` ; réutiliser les règles effectivement présentes et construire, si besoin, une variante déterministe compatible ETF/actions. Comparer avec la même méthodologie.
- [ ] **Étape 14 — Tester Mean Reversion séparément.** Adapter la logique de bandes de Bollinger de `ccxt_backtesting_example.py` (crypto) aux données actions/ETF ; valider entrées, sorties, coûts et comportements en tendances fortes.
- [ ] **Étape 15 — Ajouter les cycles d’analyse seulement si utiles.** LumiBot propose `schedule_function.py` et `register_cron_callback`. Quatre points de contrôle journaliers peuvent servir au suivi, mais **ne doivent pas imposer quatre rééquilibrages** à une stratégie quotidienne. Respecter jours fériés, fuseaux horaires, horaires d’été et séances raccourcies.
- [ ] **Étape 16 — Explorer les agents IA, sans ordre direct.** Examiner `agent_alpaca_news_builtin.py`, `agent_momentum_allocator.py`, `agent_macro_risk.py` et `ai_trading_team_ray_dalio_idea_meritocracy.py`. Tester d’abord l’IA comme analyseur ou source de propositions ; toute décision d’ordre passe par le Risk Gate et doit être comparée à la référence sans IA.
- [ ] **Étape 17 — Évaluer l’hébergement.** Uniquement après fiabilité locale, reprise après panne, gestion des secrets et fonctionnement prolongé en Paper.

**Ne pas confondre :** le filtre SMA 200 est une **variante du Momentum**, tandis que Breakout et Mean Reversion sont des **stratégies distinctes**. Le rééquilibrage, les ordres bracket et la planification sont des **composants**, pas des preuves de rentabilité.

## 7. Règles de sécurité et de qualité

-   Ne jamais utiliser de clés de trading réelles dans cette phase.
-   Ne jamais exposer les secrets dans le navigateur, Git ou les
    journaux.
-   Garder les limites de risque et la validation finale dans le backend
    Python, indépendantes de l'IA.
-   Toute proposition d'IQ doit être confrontée aux signaux et règles
    mesurables de la stratégie ; le code doit pouvoir la confirmer, la
    rejeter ou la bloquer pour examen.
-   Ne jamais envoyer un ordre sans validation explicite de toutes les
    règles ; en cas de données manquantes, périmées ou de contrôle
    incertain, ne pas envoyer de nouvel ordre.
-   L'IA ne doit jamais pouvoir contourner un rejet Python, modifier ses
    limites de risque ou appeler directement le broker.
-   Journaliser la proposition initiale, les résultats des contrôles, la
    décision Python et le statut réel de l'ordre séparément.
-   Détecter les ordres en double et tenir compte des ordres déjà
    ouverts.
-   Distinguer les données historiques, les données de marché actuelles
    et les données périmées.
-   Enregistrer les versions de stratégie et les paramètres de chaque
    backtest.
-   Éviter l'optimisation excessive des paramètres sur une seule
    période.
-   Ajouter une fonctionnalité à la fois et tester avant de poursuivre.
-   Faire un commit Git après chaque étape stable et significative.

## 8. Priorités immédiates et références

**Prochaine action unique : étape 1, puis étape 2.** Obtenir un backtest complet et reproductible avec un exemple LumiBot **inchangé**, avant toute adaptation de stratégie. Ensuite seulement : Momentum original → Top N ETF → rééquilibrage → SMA 200 → Risk Gate → comparaison → interface → Paper Trading → autres stratégies → IA.

Documents de référence :

- `docs/audit_strategies_lumibot.md` : audit détaillé rédigé par Antigravity sur le dépôt local.
- `synthese_audit_strategies_lumibot.md` : inventaire court des stratégies candidates et composants.
- `strategies_trading_mini_fonds_lumibot.md` : hypothèses de recherche, critères de comparaison et biais à éviter.

## 9. Prochain prompt à donner à Antigravity

> Nous avons déjà audité LumiBot 4.6.33 (`a5f0ee6d`). Ne refais pas l'audit complet et ne commence pas à développer une nouvelle stratégie. Ta seule mission est de faire aboutir un **backtest historique d'un exemple existant inchangé**, par exemple `stock_buy_and_hold.py`. Vérifie l'encodage UTF-8 sous PowerShell et les variables factices du `.env` signalées dans `docs/audit_strategies_lumibot.md`. Ne révèle aucune clé, ne passe aucun ordre et n'active jamais le trading réel. Diagnostique la source de données et les blocages sans laisser de processus indéfiniment suspendus. Documente la commande exacte, la période, les données, les hypothèses de coûts, les résultats et les limites. Relance le test pour vérifier sa reproductibilité. Si l'environnement exige une modification, explique-la et limite-la à la configuration nécessaire ; préserve les exemples originaux. Fournis un court compte rendu et arrête-toi après cette étape.

---

**Principe directeur :** réutiliser LumiBot, valider chaque étape avec un test réel, conserver un Risk Gate Python indépendant et rester exclusivement en backtesting / Alpaca Paper Trading pendant cette phase.
