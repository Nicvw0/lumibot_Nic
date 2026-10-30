# Stratégies de trading à évaluer pour le mini-fonds LumiBot

**Version :** 1.0  
**Date :** 29 octobre 2026  
**Marché visé :** actions américaines  
**Environnement initial :** développement local sous Windows, backtests, puis Alpaca Paper Trading  
**Principe central :** les IQ proposent des analyses et des actions ; le code Python vérifie les signaux, applique les règles de risque et décide si un ordre peut être autorisé.

---

## 1. Objectif

Identifier, tester et comparer des stratégies de trading adaptées à un petit portefeuille d'actions américaines, en utilisant LumiBot comme moteur Python.

Le but n'est pas de choisir une stratégie sur la base de promesses ou d'un rendement historique isolé. Il faut rechercher une approche :

- compréhensible et vérifiable ;
- testable sur des données historiques suffisamment fiables ;
- robuste sur différentes périodes et conditions de marché ;
- réaliste après prise en compte des coûts et des conditions d'exécution ;
- contrôlable par des règles Python indépendantes des IQ ;
- exploitable d'abord en simulation, sans argent réel.

Aucune stratégie ne garantit des gains futurs. Les résultats historiques peuvent être affectés par le surapprentissage, les biais de données et les changements de régime du marché.

## 2. Stratégies candidates

### 2.1 Momentum relatif — priorité initiale

**Principe :** classer un univers d'actions américaines selon leurs performances passées et sélectionner les actions qui ont été relativement les plus fortes.

Pistes à tester :

- calculer les performances sur plusieurs horizons, par exemple 6 et 12 mois ;
- comparer les résultats avec et sans exclusion du mois le plus récent ;
- rééquilibrer périodiquement le portefeuille ;
- imposer des critères de liquidité et de qualité des données.

**Atouts :** règles quantitatives mesurables, comparaison entre titres et fréquence de rotation contrôlable.

**Risques :** retournements rapides du marché, pertes concentrées, rotation excessive et biais de survivance si l'univers historique est mal construit.

### 2.2 Suivi de tendance — filtre de marché

**Principe :** déterminer si le marché général présente une tendance favorable. Un exemple à évaluer est la comparaison du prix d'un indice large ou d'un ETF indiciel comme SPY avec sa moyenne mobile sur 200 jours.

Versions à comparer :

- momentum sans filtre ;
- momentum avec filtre de tendance ;
- différentes définitions simples du filtre, fixées avant l'évaluation finale.

Le filtre pourrait réduire les nouvelles prises de position ou l'exposition lorsque la tendance est défavorable. Il ne doit pas être considéré comme une garantie de protection contre les baisses.

### 2.3 Cassure de prix (*breakout*) — piste ultérieure

**Principe :** ouvrir une position lorsqu'un titre dépasse un plus haut récent, éventuellement avec une confirmation par le volume et la tendance générale.

**Atouts :** peut capter des mouvements de prix marqués.

**Risques :** fausses cassures, rotations fréquentes et sensibilité aux règles d'entrée et de sortie.

À tester après avoir établi un processus de backtest fiable.

### 2.4 Retour à la moyenne (*mean reversion*) — stratégie séparée

**Principe :** rechercher des baisses de court terme anormales en supposant qu'un prix puisse revenir vers sa moyenne.

**Atouts :** logique différente de celle du momentum.

**Risques :** une baisse peut se poursuivre, notamment après une mauvaise nouvelle ou une détérioration fondamentale.

Cette approche doit d'abord être testée séparément. Elle ne doit pas contredire automatiquement un signal de momentum : les conditions précises de déclenchement et d'invalidation doivent être définies.

### 2.5 Filtres fondamentaux — évolution possible

**Principe :** filtrer les actions selon des critères de qualité financière, de rentabilité ou de valorisation, puis éventuellement appliquer le momentum au sous-ensemble retenu.

**Atouts :** peut compléter une sélection basée uniquement sur les prix.

**Risques :** données plus complexes, publication différée des états financiers, biais rétrospectif et difficultés d'accès à des données historiques correctement datées.

À envisager seulement après validation du système de base.

## 3. Première combinaison à tester

La première hypothèse de travail est un **momentum relatif avec filtre de tendance du marché et gestion du risque indépendante**.

### Étape A — Définir l'univers d'actions

- Définir une liste ou un univers d'actions américaines liquides.
- Définir à l'avance les critères d'inclusion et d'exclusion.
- Vérifier la disponibilité et la qualité des données.
- Éviter le biais de survivance : ne pas utiliser uniquement la liste des sociétés qui existent encore aujourd'hui pour simuler les choix historiques, lorsque des données historiques d'univers sont disponibles.
- Documenter les limites des données utilisées.

### Étape B — Classer les titres

- Calculer les performances historiques sur des horizons définis, par exemple 6 et 12 mois.
- Comparer plusieurs méthodes simples de classement.
- Tester séparément l'exclusion du mois le plus récent.
- Définir à l'avance le nombre de titres retenus ou la règle de sélection.
- N'autoriser aucune IQ à choisir librement des actions en contournant ces critères.

### Étape C — Filtrer selon la tendance du marché

- Choisir un indicateur de marché large et documenté.
- Tester une version sans filtre et une version avec filtre, par exemple fondé sur une moyenne mobile de long terme.
- Mesurer si le filtre améliore réellement le profil de risque hors échantillon.
- Inclure les faux signaux, les reprises rapides et les périodes latérales dans l'évaluation.

### Étape D — Appliquer la gestion du risque en Python

Le code Python doit appliquer au minimum :

- une limite de taille par position ;
- une limite d'exposition totale ;
- une limite de concentration sectorielle, si les données nécessaires sont disponibles ;
- une vérification des liquidités ;
- une vérification de la fraîcheur et de la cohérence des données ;
- une prévention des ordres dupliqués ;
- des règles de suspension et un arrêt d'urgence ;
- une politique explicite en cas d'erreur ou de résultat incertain.

Les valeurs numériques des limites doivent être définies et testées avant toute exécution. Un ordre stop ne garantit pas un prix de sortie précis lors d'une forte volatilité.

### Étape E — Choisir la fréquence

Comparer au minimum :

- un rééquilibrage hebdomadaire ;
- un rééquilibrage mensuel.

Les quatre analyses quotidiennes envisagées dans le projet peuvent surveiller le marché, les positions, les actualités et les risques sans entraîner nécessairement quatre vagues d'ordres par jour.

**Quatre analyses quotidiennes ne signifient pas quatre obligations de trader.** L'absence de transaction doit rester une décision valide.

## 4. Rôle des IQ et validation indépendante par Python

Ce principe est obligatoire pour l'architecture du projet.

### Flux décisionnel

1. Les IQ analysent les informations disponibles et peuvent proposer `BUY`, `SELL` ou `HOLD`, avec le symbole, la quantité suggérée, les raisons, les hypothèses et le niveau de confiance.
2. Le backend Python vérifie la proposition avec les données de marché, les signaux calculés, la stratégie active, les positions, les liquidités et les règles de risque.
3. Le contrôle Python retourne une décision structurée :
   - `APPROVED` : proposition autorisée ;
   - `REJECTED` : proposition rejetée, avec la raison ;
   - `REVIEW_REQUIRED` : données ou situation ambiguës, aucune exécution automatique.
4. Seule une proposition autorisée peut être transformée en ordre LumiBot/broker.
5. Le résultat côté broker est enregistré séparément : ordre soumis, accepté, rejeté, partiellement exécuté ou exécuté.

### Contrôles minimaux

- Données absentes, périmées ou incohérentes : bloquer les nouveaux ordres.
- Quantité, valeur d'ordre ou exposition dépassant les limites : rejeter ou réduire uniquement selon une règle explicite et testée.
- Liquidités insuffisantes : rejeter.
- Ordre en double ou ordre incompatible déjà ouvert : bloquer ou traiter selon une procédure idempotente.
- Stratégie en pause, mode lecture seule ou arrêt d'urgence actif : ne pas soumettre d'ordre.
- Signal de stratégie non confirmé : rejeter ou demander une nouvelle analyse, selon les règles fixées à l'avance.
- Toute modification proposée par une IQ doit être soumise à nouveau aux contrôles Python.

Le modèle d'IA ne doit pas pouvoir modifier les limites de risque, les identifiants broker ou les paramètres de sécurité. Les secrets ne doivent jamais être exposés à l'interface web.

### Journal d'audit

Pour chaque cycle, conserver :

- horodatage et mode d'exécution ;
- données et indicateurs utilisés ;
- proposition initiale de l'IQ ;
- stratégie et version de paramètres ;
- contrôles effectués et leurs résultats ;
- décision Python et raisons d'approbation ou de rejet ;
- ordre demandé et réponse du broker ;
- exécution réelle, erreurs et résultat ultérieur.

Il faut distinguer clairement **la suggestion de l'IQ**, **l'autorisation du code**, **l'ordre envoyé** et **l'exécution confirmée par le broker**.

## 5. Matrice de backtests à mettre en place

Comparer les variantes dans des conditions identiques autant que possible.

| ID | Variante | Question principale |
|---|---|---|
| A | Momentum relatif, sans filtre | La sélection par momentum apporte-t-elle un avantage face à une référence passive ? |
| B | Momentum relatif + filtre de tendance | Le filtre améliore-t-il le risque et/ou les rendements hors échantillon ? |
| C | Variante B + règles de dimensionnement du risque | Les limites de position et d'exposition améliorent-elles le profil de risque ? |
| D | Breakout indépendant | Cette stratégie mérite-t-elle d'être poursuivie après les premiers tests ? |
| E | Retour à la moyenne indépendant | Cette approche apporte-t-elle quelque chose sur un univers et des conditions définis ? |

Les variantes D et E sont des pistes secondaires. Elles ne doivent pas retarder l'établissement d'une base de comparaison solide.

### Indicateurs à enregistrer

- rendement total et annualisé ;
- maximum drawdown ;
- volatilité ;
- Sharpe ratio et Sortino ratio, en documentant leurs hypothèses ;
- nombre de transactions et rotation du portefeuille ;
- exposition moyenne et maximale ;
- coûts estimés, spreads et glissement de prix ;
- résultats par période et régime de marché ;
- comparaison à un indice de référence et à une stratégie passive simple ;
- résultats hors échantillon ;
- sensibilité à des changements raisonnables de paramètres.

Ne pas sélectionner une stratégie uniquement parce qu'elle présente le rendement historique le plus élevé.

## 6. Protocole pour éviter les backtests trompeurs

1. **Établir une référence** : comparer au S&P 500 et à une stratégie passive simple, par exemple SPY acheté et conservé, en tenant compte de la période, de l'exposition et des hypothèses.
2. **Tester chaque composant séparément** : momentum seul, filtre seul lorsque pertinent, puis combinaison.
3. **Séparer les périodes** : conception, ajustement, puis période finale de test jamais utilisée pour choisir les paramètres.
4. **Intégrer les frictions** : commissions éventuelles, spread, glissement et hypothèses d'exécution réalistes.
5. **Éviter le biais de survivance et le biais d'anticipation** : ne jamais utiliser une information avant sa date de disponibilité réelle.
6. **Tester la robustesse** : faire varier raisonnablement les paramètres et vérifier que les résultats ne dépendent pas d'un réglage très précis.
7. **Examiner les périodes difficiles** : crises, marchés baissiers, reprises brutales et marchés latéraux.
8. **Conserver les expériences** : enregistrer le code, les paramètres, les données, les résultats et la date de chaque test.
9. **Passer à Alpaca Paper Trading** seulement après des résultats suffisamment robustes et des tests satisfaisants des contrôles et de l'exécution simulée.

## 7. Architecture et étapes recommandées

LumiBot reste le moteur de stratégie et d'exécution. L'interface locale sert à visualiser les résultats, consulter le journal et piloter les fonctions autorisées. Elle ne doit pas envoyer directement d'ordres au broker.

Ordre de travail recommandé :

1. Auditer le dépôt LumiBot local, les versions et les exemples existants.
2. Reproduire un backtest de référence et vérifier les données.
3. Implémenter le momentum relatif le plus simple possible.
4. Ajouter des métriques, des tests et un journal de résultats reproductible.
5. Tester la version avec filtre de tendance.
6. Ajouter les règles de risque et tester explicitement les cas de rejet d'ordre.
7. Évaluer hors échantillon et documenter les limites.
8. Construire l'interface locale en lecture seule, puis les commandes autorisées.
9. Configurer Alpaca Paper Trading, les contrôles d'ordres, les logs et la reprise après redémarrage.
10. Ajouter les quatre cycles quotidiens en tenant compte du calendrier boursier américain, des jours fériés, des changements d'heure et des clôtures anticipées.
11. Ajouter les IQ progressivement pour l'analyse et la formulation de propositions, tout en gardant les contrôles Python indépendants.
12. N'envisager l'argent réel ou l'hébergement qu'après une phase de simulation documentée et une évaluation prudente des risques.

## 8. Sources officielles et institutionnelles

Ces sources servent de références pour la conception et les tests. Elles ne constituent pas une garantie de performance.

### LumiBot

- Documentation officielle : https://lumibot.lumiwealth.com/
- Exemples de stratégies : https://lumibot.lumiwealth.com/examples.html
- Déploiement : https://lumibot.lumiwealth.com/deployment.html

### Recherche sur le momentum et le suivi de tendance

- AQR — *Time Series Momentum* : https://www.aqr.com/insights/research/journal-article/time-series-momentum
- AQR — *A Century of Evidence on Trend-Following Investing* : https://www.aqr.com/insights/research/journal-article/a-century-of-evidence-on-trend-following-investing
- NBER — *Momentum Crashes* : https://www.nber.org/papers/w20439
- NBER — *Profitability of Momentum Strategies* : https://www.nber.org/papers/w7159

### Risque, diversification et exécution

- Investor.gov, site d'information des investisseurs de la SEC : https://www.investor.gov/
- FINRA, informations et éducation des investisseurs : https://www.finra.org/investors

### Broker et données

- Alpaca — documentation officielle : https://docs.alpaca.markets/
- Alpaca — Paper Trading : https://docs.alpaca.markets/docs/paper-trading

**Note de méthode :** avant d'implémenter une stratégie, vérifier les versions actuelles des documentations, les limites des sources de données et les conditions du compte Alpaca utilisé. Une source institutionnelle peut documenter un effet historique sans démontrer que son implémentation précise sera rentable aujourd'hui.

## 9. Recommandation finale

Commencer par trois variantes comparables :

- **Version A :** momentum relatif sur actions américaines.
- **Version B :** momentum relatif avec filtre de tendance du marché.
- **Version C :** version B avec règles explicites de dimensionnement des positions et d'exposition.

Retenir ou éliminer ces variantes sur la base de résultats reproductibles, de tests hors échantillon, des coûts et du risque. Ajouter le breakout, le retour à la moyenne, les filtres fondamentaux et les IQ uniquement lorsque la base est fiable.

**Prochaine tâche concrète :** préparer une matrice de backtests avec les paramètres, les périodes historiques, les métriques, les données nécessaires et les critères d'acceptation/rejet, puis demander à Antigravity de l'implémenter progressivement dans l'installation LumiBot existante.

---
