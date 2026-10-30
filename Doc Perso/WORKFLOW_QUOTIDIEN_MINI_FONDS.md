# Workflow quotidien du mini-fonds d’actions

Document de travail décrivant les quatre moments de la journée et la préparation de l’univers admissible.

Last Updated : 2026-10-30
Status : Conception progressive — aucune automatisation implémentée par ce document.
Audience : Propriétaire du mini-fonds et IA participant à sa conception.

## Overview

Objectif : construire un mini-fonds sur les actions américaines du S&P 500, avec quatre activations par séance. Une activation ne signifie pas qu’une transaction doit avoir lieu ; les positions peuvent être conservées plusieurs jours.

Décision validée : le contrôle complet de l’univers est effectué une seule fois par journée, avant séance. La liste produite sert de référence aux quatre moments de cette journée. Les tâches des autres moments seront précisées progressivement.

Ce document décrit notre projet personnel ; il ne constitue pas une modification du fonctionnement général de LumiBot.

## 1. Principes de fonctionnement

- Univers de départ : les actions appartenant au S&P 500, sans exclusion sectorielle automatique. Les ETF ne font pas partie de cet univers d’investissement.
- Une seule catégorie d’actions retenue par entreprise, selon une règle objective de liquidité et de disponibilité, à préciser.
- Règles explicites et contrôles reproductibles appliqués par Python ; les IA consultent les résultats, analysent et proposent des actions.
- Les IA peuvent suggérer une évolution des règles ; elles ne modifient pas seules l’univers ou ses critères.
- Un titre exclu des nouveaux achats reste suivi s’il est déjà détenu. Son exclusion ne déclenche pas automatiquement une vente.
- Les paramètres, horaires précis et sources de données restent à valider ; aucun seuil numérique n’est fixé ici.
- Pour les backtests exploratoires actuels, le guard de cash reste désactivé, conformément à la décision prise. Les contrôles futurs d’ordres décrits ici ne sont pas encore implémentés.

## 2. Moment 1 — Avant séance : constituer l’univers du jour

### Entrées nécessaires

- Composition de référence du S&P 500, avec date d’effet et source vérifiable.
- Identification des entreprises et de leurs catégories d’actions.
- Historique des prix et volumes nécessaire aux stratégies.
- Informations disponibles sur la négociabilité chez le courtier et l’achat fractionné.
- État du portefeuille : positions, liquidités et ordres en cours.
- Calendrier de marché américain et heure de référence America/New_York, y compris les séances écourtées.

### Contrôles quotidiens retenus

1. Actualiser et dater la composition de l’indice pour la séance concernée.
2. Appliquer la règle de sélection d’une catégorie d’actions par entreprise.
3. Vérifier la profondeur d’historique requise par les indicateurs utilisés.
4. Détecter les données manquantes, incohérentes ou trop anciennes, et les opérations sur titres nécessitant un traitement.
5. Vérifier la disponibilité du titre chez le courtier et les suspensions connues.
6. Évaluer la liquidité et les coûts d’exécution à partir des données disponibles, en tenant compte de la taille prévue des ordres.
7. Vérifier la compatibilité entre prix du titre, taille de position prévue et possibilité d’achat fractionné.
8. Enregistrer chaque décision d’admissibilité avec sa raison et les données utilisées.

Les informations avant ouverture ne garantissent pas les conditions de la séance à venir. Une cotation absente avant séance n’est pas, à elle seule, une preuve que le titre sera illiquide pendant les heures normales. Le traitement d’une information manquante reste à définir explicitement.

### Résultat attendu

Un état quotidien daté comprenant :

- la liste de référence du S&P 500 ;
- la liste des titres autorisés pour de nouveaux achats ;
- les exclusions, leur motif et leur caractère temporaire ou structurel ;
- les titres déjà détenus à surveiller, y compris ceux exclus des nouveaux achats ;
- les sources, la date des données et la version des règles appliquées ;
- les anomalies nécessitant une décision ou une intervention.

Trois états doivent être distingués : achat autorisé, nouvel achat interdit, négociation impossible ou suspendue selon les informations disponibles.

### Tâches de recherche et de gestion avant séance

À compléter : informations à rechercher, rôle des IA, analyse des positions et éventuelles propositions d’actions.

## 3. Moment 2 — Après ouverture

Référence : univers quotidien préparé avant séance. Pas de nouveau filtrage complet de l’univers.

À compléter :

- heure ou délai après ouverture ;
- informations à examiner ;
- rôle de chaque IA ;
- décisions possibles et conditions d’intervention ;
- compte rendu à enregistrer.

## 4. Moment 3 — Milieu de séance

Référence : univers quotidien préparé avant séance. Pas de nouveau filtrage complet de l’univers.

À compléter :

- horaire ;
- suivi du portefeuille et informations nouvelles ;
- rôle de chaque IA ;
- décisions possibles et conditions d’intervention ;
- compte rendu à enregistrer.

## 5. Moment 4 — Avant clôture

Référence : univers quotidien préparé avant séance. Pas de nouveau filtrage complet de l’univers.

À compléter :

- délai avant clôture, adapté aux séances écourtées ;
- revue des positions et des ordres en cours ;
- conditions de conservation pendant la nuit ;
- rôle de chaque IA et décisions possibles ;
- bilan et préparation de la séance suivante.

## 6. Contrôle d’un ordre : couche distincte de l’univers quotidien

Le filtrage quotidien définit les candidats possibles. Il ne garantit pas qu’un ordre concret sera exécutable plusieurs heures plus tard.

Architecture envisagée, à détailler et valider avant implémentation : juste avant l’envoi d’un ordre, Python vérifie sa conformité à l’univers du jour et les conditions d’exécution pertinentes, notamment disponibilité du titre, prix, quantité, ordres déjà en cours, fonds disponibles et limites du portefeuille.

Ce contrôle d’ordre ne reconstruit pas l’univers. Un événement en séance, tel qu’une suspension ou une perte de données, peut imposer de bloquer une nouvelle entrée. Le traitement de ces événements, ainsi que la gestion des sorties d’un titre devenu inadmissible, restent à définir.

## 7. Reproduction en backtest

- Utiliser la composition du S&P 500 connue à chaque date simulée, et non uniquement sa liste actuelle.
- Conserver le suivi des titres sortis de l’indice, radiés, fusionnés ou renommés et traiter leurs événements.
- Appliquer les filtres avec les seules informations disponibles au moment simulé ; ne pas utiliser les volumes ou les prix futurs de la séance.
- Conserver la même distinction entre univers quotidien et contrôles d’ordres.
- Documenter les données indisponibles et les approximations au lieu de supprimer silencieusement les cas difficiles.
- La simulation des quatre moments nécessite des données et une horloge adaptées ; les modalités techniques restent à définir.

## 8. Prochaines décisions à prendre

1. Source de composition actuelle et historique du S&P 500.
2. Sources des données de prix, volumes, cotations et événements sur titres.
3. Règle de choix entre catégories d’actions d’une entreprise.
4. Historique minimal propre à chaque stratégie et traitement des nouveaux membres.
5. Seuils de liquidité, de coût et de fraîcheur, adaptés au capital et à la taille des ordres.
6. Comportement si les données ou le contrôle avant séance sont indisponibles.
7. Règles de gestion des positions exclues et des événements en séance.
8. Contenu précis des quatre moments, responsabilités des IA et contrôles d’ordres.

## 9. Sources de référence

- S&P Dow Jones Indices — S&P 500 : https://www.spglobal.com/spdji/en/indices/equity/sp-500/
- SEC / Investor.gov — Liquidité : https://www.investor.gov/introduction-investing/investing-basics/glossary/liquidity-or-marketability
- Alpaca — Modèles des actifs et attributs de négociabilité : https://alpaca.markets/sdks/python/api_reference/trading/models.html
- QuantConnect — Biais de survivance : https://github.com/QuantConnect/Documentation/blob/master/03%20Writing%20Algorithms/01%20Key%20Concepts/10%20Research%20Guide/08%20Survivorship%20Bias.html

## 10. Mécanique Python et agents : réutiliser LumiBot

### Règle de conception impérative

Réutiliser en priorité les fonctions existantes de LumiBot. Ne pas recréer un moteur d’agents, un ordonnanceur, un système de mémoire, un moteur de backtest ou une connexion de courtage déjà fournis par la bibliothèque.

Avant chaque développement, identifier la fonction native disponible, examiner son fonctionnement dans la version locale et vérifier qu’elle répond au besoin. Adapter notre stratégie personnelle autour de cette fonction. Si une capacité manque réellement, documenter le besoin et l’écart avant de proposer une extension ; ne pas modifier le cœur de LumiBot implicitement.

Vérification initiale : lecture du code et de la documentation de LumiBot 4.6.33 le 2026-10-30. Cette vérification décrit les possibilités existantes ; elle ne constitue pas une qualification par exécution de notre futur mini-fonds.

### Fonctions existantes à réutiliser

| Besoin | Fonction ou composant LumiBot | Usage prévu dans le mini-fonds |
|---|---|---|
| Héberger notre logique | Classe `Strategy` et ses paramètres | Une stratégie personnelle porte les règles, le contexte et l’orchestration. |
| Préparation avant séance | `before_market_opens()` et `minutes_before_opening` | Préparer et contrôler une fois l’univers quotidien. |
| Travail pendant la séance | `on_trading_iteration()`, `sleeptime`, `get_datetime()` | Déclencher les moments prévus selon l’heure de la stratégie, avec un état empêchant les doublons. Les modalités restent à valider. |
| Préparation avant clôture | `before_market_closes()` et `minutes_before_closing` | Organiser le quatrième moment selon le calendrier et les séances écourtées. |
| Créer des agents | `self.agents.create(...)` | Définir leurs rôles, modèles, outils et permissions explicitement. |
| Appeler et coordonner les agents | `.run(task_prompt=..., context=...)` et `self.agents.run_together(...)` | Transmettre le contexte et les résultats ; paralléliser seulement les analyses indépendantes si utile. |
| Recevoir une proposition structurée | `output_schema`, `result.parsed`, `result.parse_error` | Recevoir un résultat contrôlable par Python et refuser une proposition mal formée. |
| Lire le marché et le compte | API publiques de `Strategy` et outils intégrés des agents | Réutiliser prix, historiques, indicateurs, positions et ordres disponibles ; vérifier les connexions et données nécessaires. |
| Ajouter un outil propre à notre stratégie | `@agent_tool` si nécessaire | Exposer une fonction manquante après avoir vérifié les outils natifs ; déclarer correctement ses effets sur le trading. |
| Dimensionner et exécuter | Fonctions de dimensionnement existantes si adaptées, `create_order()`, `submit_order()` et suivi natif des ordres | Utiliser la chaîne d’exécution normale après validation de nos règles. |
| Conserver le contexte et la justification | `self.vars`, mémoire native SQLite, outils de mémoire et traces d’agents | Stocker l’état nécessaire, les propositions, décisions et thèses sans recréer une mémoire parallèle. La reprise après redémarrage devra être qualifiée. |
| Tester historiquement | Backtesting natif, horloge simulée, traces et cache de rejeu des agents | Comparer les comportements sur des données historiques et conserver les preuves. |

`run_together()` fait se chevaucher les appels aux modèles ; les appels d’outils et les opérations sur l’état partagé sont sérialisés par LumiBot. Ce n’est pas un mécanisme destiné à multiplier les exécuteurs d’ordres indépendants.

### Architecture retenue pour la conception

1. Avant séance, Python prépare l’univers admissible une fois, selon les règles validées.
2. À chacun des quatre moments, Python prépare un contexte daté : univers du jour, positions, ordres en cours, informations nécessaires et éléments utiles des analyses précédentes.
3. Les agents analysent et proposent acheter, vendre, réduire, conserver ou ne rien faire, dans un format structuré.
4. Python valide la proposition : structure, informations nécessaires, admissibilité du titre, cohérence avec les positions et ordres, quantités et limites du portefeuille.
5. Python soumet uniquement les ordres validés par les méthodes normales de LumiBot.
6. Le système suit les statuts réels des ordres et enregistre les décisions et résultats avec les composants natifs.

Point de départ recommandé, à préciser avec les tâches de chaque moment : un agent analyste et un agent de décision, tous deux sans permission de trading direct. Ajouter un contradicteur ou des spécialistes seulement si leur utilité est démontrée. Le contenu des analyses et les règles financières restent à définir.

### Permissions et contrôles

- Configurer explicitement `allow_trading=False` pour tous les agents de cette architecture. Dans la version inspectée, l’omission de ce paramètre autorise le trading par défaut.
- Autoriser les outils réseau aux agents qui en ont besoin, par la configuration native. L’existence d’un outil n’implique pas que la connexion, les données ou l’autorisation nécessaires soient disponibles.
- Les outils personnalisés doivent déclarer correctement leurs effets ; une fonction qui envoie un ordre ne doit pas être présentée comme une simple lecture.
- Une consigne dans un prompt ne remplace pas une vérification Python. Le format structuré valide la forme de la réponse, pas la vérité des données ni la pertinence financière.
- Ne pas donner le droit de négocier directement à un agent en comptant bloquer son résultat après `.run()` : les outils peuvent déjà avoir envoyé des ordres pendant cet appel.
- Les vérifications natives des outils d’ordres des agents contrôlent notamment la consultation du compte, des positions, des ordres et des prix. Elles ne constituent pas notre politique complète de risque et ne garantissent pas nos plafonds ou l’absence de cash négatif.
- Notre choix d’exécution Python ne doit pas supposer que les contrôles spécifiques aux outils des agents se déclenchent automatiquement : nos vérifications propres restent à implémenter et qualifier.
- Un ordre soumis n’est pas un ordre exécuté. Distinguer attente, exécution partielle, exécution complète, annulation et rejet. Après une réponse incertaine, réconcilier les ordres et positions avant de réessayer pour éviter un doublon.
- La décision actuelle de laisser le guard de cash désactivé en backtest exploratoire reste inchangée. Les contrôles décrits ici sont une conception future, pas une protection déjà active.

### Planification et limites des backtests

- Réutiliser les points d’entrée natifs avant ouverture et avant clôture, puis la boucle normale de stratégie pour les autres moments.
- `register_cron_callback()` existe pour les exécutions hors backtest, mais ne fait rien en backtest dans la version inspectée. Ne pas construire les quatre moments historiques uniquement avec cette fonction.
- Utiliser l’heure simulée de LumiBot, le calendrier de marché et des données suffisamment détaillées pour les événements et les prix nécessaires. Des barres quotidiennes seules ne reproduisent pas les quatre moments intrajournaliers.
- Définir la prévention des appels ou ordres en double, la durée maximale d’un cycle, les retards et la reprise après interruption avant exécution réelle.
- Les protections contre les informations futures et les dates simulées ne garantissent pas qu’un modèle ignore tous les événements historiques appris pendant son entraînement. Documenter cette limite et contrôler les sources utilisées.
- Les appels IA ont un coût et peuvent produire des réponses différentes. Le cache natif peut rejouer des résultats compatibles ; il ne démontre ni la qualité financière ni la robustesse d’une stratégie.

### Ce qui reste propre à notre mini-fonds

- La source vérifiable de composition actuelle et historique du S&P 500 et sa mise à jour.
- Les paramètres et filtres d’admissibilité de notre univers.
- Les tâches et horaires des quatre moments.
- Les instructions des agents et le format de leurs propositions.
- Les contraintes de portefeuille, la validation des propositions et les cas de refus.
- Les tests de notre orchestration, des exclusions, des ordres et de la reprise.

Ces éléments doivent être réalisés dans les fichiers de notre stratégie et sa configuration, en utilisant les interfaces publiques de LumiBot. Les exemples fournis servent de références ; ils ne sont pas des stratégies validées pour notre objectif et ne doivent pas être copiés sans examiner leurs permissions et leur univers.

### Références locales examinées

Chemins relatifs à la racine du dépôt LumiBot :

- `docsrc/agents_flows.rst` : fonctionnement hybride, coordination et exécution Python.
- `docsrc/agents_memory.rst` : mémoire, thèses, journal et limites des protections.
- `docsrc/agents_builtin_tools.rst` : outils intégrés, permissions et vérifications avant ordre des agents.
- `docsrc/agents_observability.rst` : traces et rejeu des appels.
- `lumibot/components/agents/manager.py` : création, permissions, appels et coordination.
- `lumibot/components/agents/structured_output.py` : validation des réponses structurées.
- `lumibot/components/agents/builtins.py` : outils de marché, de compte et d’ordres.
- `lumibot/strategies/strategy.py` : points d’entrée du cycle de vie, ordres et planification.
- `lumibot/example_strategies/ai_researcher_trader.py` : recherche puis décision avec un agent autorisé à négocier ; référence d’organisation, permissions différentes de notre architecture retenue.
- `lumibot/example_strategies/ai_trading_team_bull_bear_large_cap_stocks.py` : recherche, débat et décision sur une liste fixe ; ne couvre pas notre univers historique ni les quatre moments.

## 11. Organisation des fichiers et déclenchement des quatre moments

### Organisation validée

Un fichier par responsabilité, et non un fichier de code par jour. Le même code est réutilisé à chaque séance ; les données et journaux portent une date. Les noms ci-dessous sont indicatifs, pas des fichiers déjà créés.

| Élément | Responsabilité |
|---|---|
| Stratégie principale | Une seule sous-classe `Strategy` coordonne les quatre moments, les agents, le portefeuille et la chaîne d’exécution LumiBot. |
| Module avant séance | Récupération et contrôle de l’univers quotidien, préparation du contexte et tâches de recherche à définir. |
| Module après ouverture | Tâches propres au deuxième moment, à préciser. |
| Module milieu de séance | Tâches propres au troisième moment, à préciser. |
| Module avant clôture | Tâches propres au quatrième moment, à préciser. |
| Définition des agents | Rôles, instructions, outils autorisés et schémas de réponse ; agents créés par le gestionnaire natif LumiBot. |
| Contrôles communs | Vérification des propositions et contraintes propres au mini-fonds ; exécution via les méthodes natives. |
| Configuration | Horaires, paramètres, seuils et limites validés. |
| Données du projet | Copies de la composition de l’indice, résultats des contrôles et univers admissibles datés. Réutiliser la mémoire et les traces natives pour les activités des agents. |

Les modules de phase sont de simples fonctions Python appelées par la stratégie principale. Ils ne démarrent ni robot, ni courtier, ni ordonnanceur indépendant. Ils travaillent dans le contexte de la même stratégie et du même compte. Les calculs, contrôles et instructions partagés sont centralisés pour éviter les divergences entre phases.

Le nombre exact de fichiers doit rester proportionné au besoin : une fonction courte peut rester dans la stratégie jusqu’à ce qu’une séparation améliore sa lisibilité. Une séparation en fichiers n’apporte pas, à elle seule, de capacité supplémentaire.

### Ce qui est déjà préparé dans LumiBot

Examen local effectué le 2026-10-30 :

- `Strategy` possède les points d’entrée `initialize()`, `before_market_opens()`, `before_starting_trading()`, `on_trading_iteration()`, `before_market_closes()` et `after_market_closes()`.
- La boucle et le calendrier sont pris en charge par l’exécuteur de stratégie. Réutiliser l’heure de la stratégie et les informations d’ouverture et de clôture plutôt que créer un calendrier indépendant.
- La préparation peut être raccordée à `before_market_opens()`, le quatrième moment à `before_market_closes()`. Les moments après ouverture et milieu de séance nécessitent notre logique de déclenchement dans la boucle normale. `before_starting_trading()` intervient après ouverture, sans être une garantie d’un délai arbitraire choisi après celle-ci.
- `self.vars` permet de conserver l’état de la stratégie. Des mécanismes natifs de sauvegarde et de restauration existent, notamment pour l’exécution planifiée. Leur configuration et leur fonctionnement dans notre futur lancement local doivent être vérifiés avant de promettre une reprise après redémarrage.
- Le gestionnaire d’agents, leur coordination, la mémoire et les ordres existent déjà ; leur séparation dans nos fichiers est un choix d’organisation, pas une raison de recréer ces composants.
- L’exemple `schedule_function.py` illustre `register_cron_callback()` en paper trading. Cette fonction ignore les inscriptions en backtest et ne suffit donc pas comme base commune de nos quatre moments.
- Le mode `run_live(run_once=True)` existe : une exécution ponctuelle suivie du traitement nécessaire des travaux d’ordres. Il ne crée pas automatiquement les quatre rendez-vous et n’est pas une API de progression pas à pas du backtest.
- Des fonctions d’exécution planifiée existent pour les intégrations BotSpot/BotManager, avec heure cible et état restauré. Elles ne constituent pas une installation locale déjà configurée pour notre mini-fonds.
- `on_closed_market_iteration()` couvre une préparation spécifique hors marché dans le mode planifié correspondant ; les mutations d’ordres prises en charge y sont bloquées. Ce point d’entrée n’est pas interchangeable avec toute la préparation avant séance sans vérifier le mode de lancement.

Aucun modèle prêt à l’emploi correspondant exactement à nos quatre moments et à notre univers S&P 500 n’a été identifié dans les fichiers examinés. Les exemples d’équipes IA montrent surtout des orchestrations contenues dans une classe ; leur logique peut guider notre assemblage sans reprendre leurs univers ou permissions tels quels.

### Mode recommandé pour commencer

Recommandation technique, à qualifier avant implémentation : garder une seule stratégie en fonctionnement continu durant les séances, avec une boucle LumiBot suffisamment fréquente et des agents appelés uniquement aux quatre moments prévus. Quatre activations d’analyse ne signifient pas seulement quatre passages de la boucle technique.

Prévoir un état par date de séance et par moment, distinguer début et fin de traitement, et définir le comportement en cas de retard, d’échec ou de reprise. Un simple indicateur de phase terminée ne suffit pas à garantir l’absence de doublons d’ordres après interruption : réconcilier aussi les positions et ordres du courtier.

Le mode ponctuel pourra être réexaminé si nous souhaitons arrêter complètement le processus entre les moments. Réutiliser alors les mécanismes natifs de lancement et de persistance avant d’envisager une infrastructure supplémentaire.

### Références locales complémentaires

- `docsrc/strategy_api_overview.rst` : stratégie, exécution continue et mode ponctuel.
- `docsrc/lifecycle_methods.rst` et `lumibot/strategies/strategy.py` : points d’entrée de la séance.
- `lumibot/strategies/strategy_executor.py` : déclenchement des événements et boucle.
- `lumibot/strategies/scheduled_timing.py` : suivi temporel des exécutions planifiées.
- `docsrc/environment_variables.rst`, section Live scheduled execution : paramètres de lancement et persistance du mode planifié.
- `docsrc/common_mistakes.rst`, section Restoring Asset Variables After a Restart : restauration des objets de stratégie.
- `lumibot/example_strategies/schedule_function.py` : exemple cron en paper trading, pas un modèle de backtest intrajournalier.

## 12. Récupération quotidienne du fichier S&P 500 — décision validée

Source retenue comme base de travail pour l’univers actuel : CSV du dépôt `datasets/s-and-p-500-companies`, issu de Wikipédia. Ce n’est pas une source officielle de composition ni un historique complet.

Adresse de téléchargement : https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv

1. Avant séance, la stratégie utilise son point d’entrée natif LumiBot pour déclencher une fonction Python de récupération. Aucun ordonnanceur séparé n’est nécessaire dans le mode continu recommandé.
2. Contrôler le format, les colonnes requises, l’unicité des symboles, un nombre plausible de titres et les variations par rapport à la dernière copie validée. Définir les seuils avant implémentation ; ne pas imposer exactement 500 lignes.
3. Conserver la copie brute, l’heure de récupération, la source et le résultat des contrôles. Archiver les versions datées sans écraser les précédentes.
4. Appliquer nos filtres pour produire l’univers admissible du jour, distinct du fichier brut.
5. Fournir le même univers aux agents aux quatre moments et aux contrôles Python des propositions.

La date du dernier changement GitHub ne suffit pas à prouver la fraîcheur : l’automatisation du dépôt prévoit une exécution quotidienne et ne crée un commit que si les données changent. La récupération du CSV ne prouve pas non plus que son contenu a été vérifié récemment. Le contrôle de fraîcheur doit tenir compte de ces distinctions.

En cas d’échec, conserver la dernière copie valide et signaler son ancienneté. La durée d’acceptation d’une copie précédente et les conditions de blocage des nouveaux achats restent à définir ; aucun repli automatique sans limite n’est décidé.

Ne pas reprendre le script d’extraction Wikipédia du dépôt par défaut : réutiliser le CSV publié, puis nos contrôles locaux. Les archives collectées à partir de maintenant ne reconstruisent pas les compositions historiques 2021–2025. La recherche d’une source historique reste une tâche distincte.

## 13. Plusieurs stratégies disponibles, une seule active en live

### Décision validée

Le mini-fonds peut contenir plusieurs stratégies et plusieurs jeux de paramètres. Une seule stratégie, dans une version et une configuration explicitement sélectionnées, est autorisée à négocier sur le compte réel. Des backtests d’autres stratégies ou réglages peuvent être exécutés en parallèle sans modifier la stratégie live.

Aucune stratégie n’est autorisée à se promouvoir automatiquement en live à partir de ses résultats. L’activation réelle et le remplacement de la stratégie active nécessitent une décision explicite du propriétaire.

### Existant LumiBot vérifié

Lecture du code local 4.6.33 le 2026-10-30 :

- Une stratégie est une sous-classe de `Strategy`, avec ses paramètres. Le même code peut utiliser les interfaces natives de backtest ou le lancement `run_live()` selon le mode choisi.
- `Trader.add_strategy()` accepte l’ajout d’une stratégie, mais `Trader.run_all()` exige actuellement exactement une stratégie : plusieurs stratégies live sont refusées, et plusieurs stratégies dans un même backtest le sont également.
- `Trader.run_all()` interdit de mélanger brokers de backtest et exécution live dans le même lanceur.
- Cette limitation est locale au lanceur. Elle n’empêche pas deux processus ou deux machines de lancer chacun une stratégie sur le même compte. Elle ne remplace pas un mécanisme d’exclusivité du compte.
- Les paramètres de stratégie, le broker simulé, la mémoire et les artefacts de backtest existent déjà. Il faut configurer leur séparation, sans recréer leurs moteurs.
- Une FAQ locale décrit encore plusieurs stratégies dans un `Trader`. Pour la version inspectée, cette indication contredit la vérification explicite dans `trader.py` ; notre conception suit le code réellement présent.

Références : `lumibot/traders/trader.py` (`add_strategy`, `run_all`), `lumibot/strategies/strategy.py` (`run_live`, `backtest`, gestion des paramètres), `docsrc/faq.rst` (entrée sur les stratégies simultanées à considérer avec cette réserve).

### Organisation proposée

- Un catalogue simple associe un identifiant de stratégie à sa classe Python et à ses configurations. Ce catalogue sert à sélectionner des stratégies existantes, pas à créer un nouveau moteur de trading.
- Chaque stratégie possède ses règles de sélection, d’entrée, de sortie et ses paramètres. Elle réutilise notre infrastructure commune des quatre moments si cela correspond à son fonctionnement.
- Les fonctions communes restent centralisées : calendrier via LumiBot, univers S&P 500, admissibilité, préparation du contexte, validation des propositions et exécution par LumiBot.
- Les paramètres propres à une stratégie restent distincts des règles communes du mini-fonds ; les expériences peuvent modifier ces paramètres sans modifier silencieusement les règles live.
- Un lanceur live explicite charge uniquement la stratégie sélectionnée et sa configuration figée, puis utilise `run_live()`.
- Un lanceur de backtest explicite sélectionne une stratégie, ses paramètres, sa période et sa source historique, puis utilise le moteur de backtest LumiBot. Il n’instancie pas le broker réel et ne reçoit pas les identifiants de trading live.
- Les lancements live et backtest utilisent des processus séparés. Plusieurs expériences simultanées nécessitent des processus distincts, et des ressources disponibles suffisantes.

### Protection de la version live et séparation des états

- Identifier la version live par une révision de code figée ou un paquet de déploiement identifié, avec la configuration et les instructions des agents effectivement utilisées. Éditer le dossier de recherche ne doit pas modifier les fichiers lus par le live.
- Inclure aussi les modules communs, les dépendances et les paramètres dans cette séparation. Un processus Python déjà démarré ne garantit pas à lui seul cette isolation : il peut relire des fichiers, importer des modules plus tard ou redémarrer.
- Ne pas appliquer automatiquement les mises à jour de paramètres ni le rechargement des prompts au live ; préparer et valider une nouvelle version avant activation explicite.
- Séparer les espaces de mémoire, les états de séance, les journaux, les résultats et fichiers temporaires du live et de chaque expérience. Utiliser les options natives de stockage et des noms ou répertoires de lancement distincts. Une leçon issue d’un backtest ne doit pas être injectée dans la mémoire live par accident.
- Réutiliser les caches de données et de rejeu lorsqu’ils sont compatibles et sûrs ; ne pas dupliquer ou effacer les caches partagés sans nécessité. Leur partage éventuel n’autorise pas le partage des décisions ou états mutables.
- Prévoir un verrou d’exécution associé au compte, avec gestion de sa libération et de la reprise. Un verrou local couvre seulement l’hôte concerné ; un second serveur nécessite une exclusivité coordonnée ou l’arrêt garanti de l’autre lancement.
- Les backtests sont isolés des accès de trading réel. Les éventuels identifiants nécessaires à la lecture des données doivent être traités séparément. Des agents en backtest ne doivent pas recevoir d’outil personnalisé ou de connexion externe capable de négocier sur le compte réel.
- Préserver les ressources du live : limiter le nombre de backtests et les appels IA concurrents ; séparer davantage les environnements si le processeur, la mémoire ou les quotas perturbent les cycles live.

### Changement de stratégie active

1. Valider la stratégie candidate et sa configuration en backtest, puis en paper trading avant activation réelle.
2. Préparer la version exacte à activer et obtenir la décision explicite du propriétaire.
3. Mettre l’ancienne stratégie à l’arrêt de façon contrôlée, examiner les ordres en cours et réconcilier l’état réel du compte.
4. Décider explicitement du traitement des positions existantes : reprise par la nouvelle stratégie ou sortie organisée. Ne pas vendre automatiquement tout le portefeuille pour simplifier le remplacement.
5. Libérer puis reprendre l’exclusivité du compte sans chevauchement des deux exécuteurs. Charger l’état de départ contrôlé et conserver la trace du changement.
6. Vérifier le démarrage et le comportement de la nouvelle version. Prévoir une procédure de retour arrière qui tient compte des ordres et positions réellement présents, sans restaurer aveuglément un ancien état.

### Ordre d’implémentation envisagé

1. Définir les fichiers communs et une première stratégie de référence, avec les interfaces natives LumiBot.
2. Mettre en place la sélection explicite et le lancement exclusivement en backtest au départ.
3. Ajouter une seconde stratégie ou un second jeu de paramètres pour vérifier la séparation des expériences.
4. Préparer le lancement paper, l’isolation des versions et états, l’exclusivité du compte et les règles de reprise.
5. Qualifier le fonctionnement simultané paper et backtest, les redémarrages, les refus d’un second lancement et le remplacement contrôlé.
6. Activer une seule version live uniquement sur autorisation explicite, après validation.

Cette section documente l’architecture. Aucun lanceur, verrou, catalogue ou déploiement live n’est créé par cette mise à jour.

## 14. État du squelette créé — 2026-10-30

Périmètre corrigé et validé : architecture vide uniquement, sans stratégie concrète, profil d’observation, signal, agent, collecte S&P 500 ou lancement de trading. Les sections précédentes décrivent la cible ; leurs étapes de raccordement ne sont pas réalisées par cette création.

Dossier créé : `mini_fund/`, hors du cœur `lumibot/`.

- `strategies/` : catalogue vide et base abstraite dérivée de `Strategy`. Les raccords avant ouverture et avant clôture réutilisent les points d’entrée natifs. La répartition des deux moments intermédiaires reste abstraite, sans horaire ni ordonnanceur supplémentaire.
- `phases/` : quatre modules réservés aux quatre moments. Leurs fonctions signalent explicitement que les tâches ne sont pas implémentées.
- `common/contracts.py` : noms des quatre moments et contrat de contexte. Un univers non préparé est représenté par `None`, sans simuler une validation.
- `agents/`, `universe/`, `execution/` : emplacements réservés, sans logique métier.
- `config/application.json` : stratégie live, horaires et source d’univers laissés non définis. Le fuseau de référence est America/New_York.
- `runners/` : points d’entrée séparés live et backtest, explicitement non raccordés. Aucun broker ou moteur d’exécution n’est instancié.
- `runtime/` : emplacement réservé aux futurs états isolés, avec exclusion des fichiers générés du suivi Git. Ce dossier ne fournit pas encore sauvegarde, verrou ou reprise.
- `ui/index.html` : page web statique montrant les emplacements futurs et l’absence de données. Aucun accès réseau, backend ou bouton d’exécution ; ce n’est pas encore un suivi de processus.
- `__main__.py` : commande d’inspection en lecture seule, `python -m mini_fund`, qui ne charge pas LumiBot et ne démarre rien.
- `README.md` : structure, réutilisation et limites décrites.

Réutilisation vérifiée avant création : classe `Strategy`, points d’entrée de séance et horloge, `Trader` et ses restrictions, gestionnaire d’agents, mémoire et rapports natifs. Aucune interface de pilotage locale prête à reprendre n’a été identifiée dans les sources examinées ; la page vide respecte le choix d’une interface web locale. Les rapports natifs HTML devront être réutilisés lors du raccordement des résultats.

Vérifications réalisées : syntaxe des 17 modules Python, inspection du catalogue vide et des paramètres non définis, refus explicite des six points d’entrée non raccordés (deux lanceurs et quatre phases), absence d’import LumiBot pendant ces contrôles. Pas de backtest, d’appel IA, de connexion broker ni d’ordre. L’intégration d’une stratégie réelle et les protections live restent à qualifier lors des étapes correspondantes.

La première extension prévue est l’acquisition du S&P 500, à réaliser séparément sur instruction. L’implémentation de la structure ne vaut pas autorisation d’activer le live.

## 15. Déclencheurs raccordés — horaires à décider

La mécanique des déclencheurs est ajoutée dans `mini_fund/common/triggers.py` et
raccordée à la base abstraite `mini_fund/strategies/base.py`, sans stratégie
concrète ni tâche métier. Les quatre horaires restent `null` et donc désactivés.
La commande d’inspection affiche aussi les paramètres techniques des déclencheurs.

- Réutilisation de la boucle, des événements et de l’heure LumiBot, avec son
  calendrier natif NYSE ; aucun cron ou ordonnanceur supplémentaire.
- Référence de séance America/New_York ; événements techniques en UTC.
- Horaires futurs exprimés par décalage relatif à l’ouverture ou à la clôture.
  La clôture anticipée est donc prise en compte. Un horaire intrajournalier hors
  séance est signalé sans exécution ni déplacement implicite.
- Cadence technique demandée : une seconde. Cette cadence n’est pas une garantie
  de précision réelle ; les tâches longues et la résolution des données peuvent
  retarder les appels.
- Tolérance de retard laissée non définie ; elle doit être choisie explicitement
  avant d’activer un horaire. Au-delà, le moment est marqué manqué, sans rattrapage.
- Registre par date et moment dans `self.vars`, marqué avant le début du travail,
  avec états running/completed/failed/missed/outside_session. Pas de nouvel appel
  automatique après un échec ou une entrée déjà enregistrée.
- Les tâches restent séquentielles. L’heure est relue avant chaque phase pour
  constater un retard éventuel après une tâche longue.
- La prévention des doublons couvre le processus et un registre effectivement
  restauré. La persistance native doit encore être configurée et qualifiée ;
  l’exclusivité entre plusieurs processus n’est pas implémentée.

21 vérifications passent : quatre appels uniques, retards admis ou manqués,
échec sans nouvel essai, appel récursif, nouveau jour, reprise d’un état connu,
heure d’été/hiver, séances écourtées et absence de séance. Les tests de raccordement
utilisent les événements et le calendrier réel LumiBot sans construire de broker.
Le 3 juillet 2025 est confirmé à 13 h et le 4 juillet sans séance. Ces tests ne
constituent pas une qualification de précision en live ni un backtest complet.

La prochaine décision porte sur les horaires, la tolérance, le traitement des
moments manqués et l’adaptation souhaitée des moments intermédiaires aux séances
écourtées. L’acquisition S&P 500 et le contenu des tâches restent non implémentés.
Aucun processus de trading ou appel IA n’est démarré par cette modification.

## 16. Horaires validés et configurés — 2026-10-30

Cette décision remplace les horaires non définis des sections historiques 14 et 15.
Les heures sont celles du début des tâches ; elles n’imposent aucune transaction.

| Phase | Règle | Séance 9 h 30–16 h | Séance 9 h 30–13 h |
|---|---|---|---|
| Avant séance | Ouverture moins 30 minutes | 9 h 00 | 9 h 00 |
| Après ouverture | Ouverture plus 45 minutes | 10 h 15 | 10 h 15 |
| Milieu de séance | Milieu exact de la séance | 12 h 45 | 11 h 15 |
| Avant clôture | Clôture moins 30 minutes | 15 h 30 | 12 h 30 |

Référence : America/New_York, avec changements d’heure. Journaux en UTC.
Le calendrier natif LumiBot fournit les séances effectives : pas de déclenchement
les week-ends ou jours fériés ; adaptation aux clôtures anticipées. L’ancre
`midpoint` calcule le milieu réel, sans décalage fixe après ouverture.

Configuration : `mini_fund/config/application.json`. Les quatre moments sont
configurés ; aucune stratégie concrète ou processus permanent n’est lancé.
Les tâches métier et le lanceur restent à raccorder ultérieurement.

Réglage technique initial retenu pour rendre la configuration utilisable :
contrôle demandé chaque seconde et tolérance de démarrage de 60 secondes,
borne incluse. Au-delà, le moment est manqué sans rattrapage automatique.
Cette tolérance est ajustable ; elle ne garantit ni l’exécution à la seconde
ni une durée maximale des tâches.

Motifs du choix :
- 9 h : intégrer les publications de 8 h 30 et laisser trente minutes de préparation.
- 10 h 15 : observer l’ouverture et laisser une marge après les publications de 10 h.
- 12 h 45 : point de gestion à mi-séance, sans avantage de rendement présumé.
- 15 h 30 : garder du temps pour l’analyse, les ordres éventuels et leur vérification.

Les journées FOMC demandent de considérer l’annonce généralement à 14 h et la
conférence à 14 h 30 dans les futures tâches. Aucun cinquième déclencheur ni
déplacement automatique particulier n’est ajouté. Le calendrier de Bourse
ne remplace pas un calendrier d’annonces économiques.

Sources examinées lors de la proposition :
- NYSE : https://www.nyse.com/trade/trading-information
- BLS : https://www.bls.gov/schedule/2026/
- NYSE, ouverture : https://www.nyse.com/data-insights/opening-auction-filling-behaviors-opportunities-early-in-the-day
- ISM : https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar
- Federal Reserve Bank of Kansas City : https://www.kansascityfed.org/research/economic-review/estimating-the-effects-of-monetary-policy-an-ongoing-evolution/

La carte « Les 4 rendez-vous du fonds » dans `mini_fund/ui/index.html` affiche
les séances normales et les clôtures à 13 h. C’est une présentation statique
du planning, pas un indicateur d’exécution ou de connexion au compte.

Validation : 23 vérifications hors ligne réussies, dont les quatre heures validées
en séance normale et écourtée via le calendrier natif, et la tolérance à 60 secondes
avec refus à 61 secondes. Aucun ordre ni appel IA. Aucun changement du cœur LumiBot.
