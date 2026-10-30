# Stratégies à évaluer — Mini-fonds d'actions du S&P 500

Protocole de recherche et état réel des exemples LumiBot, après les décisions du projet.

**Version :** 2.0  
**Dernière mise à jour :** 30 octobre 2026  
**Statut :** base de mise au point en backtesting ; aucune stratégie S&P 500 finale sélectionnée  
**Public :** propriétaire du projet et agents chargés des recherches et tests

## 1. Objectif et décisions en vigueur

Construire progressivement un mini-fonds d'**actions individuelles du S&P 500**, marché américain, avec LumiBot comme moteur. Commencer par des backtests vérifiables, puis envisager Alpaca Paper Trading après qualification de l'exécution et des risques.

Décisions validées :

- L'univers autorisé est le **S&P 500**, avec ses membres à la date simulée. Les ETF ne constituent plus le portefeuille cible. SPY peut rester un benchmark ou un indicateur de marché.
- Le fonctionnement comporte **quatre activations par séance normale** : avant ouverture, après ouverture, en cours de séance et avant clôture. Les heures exactes restent à fixer. Chaque activation peut conclure à `HOLD` ou à aucun ordre ; elle ne force pas un rééquilibrage.
- La base de comparaison comprend d'abord **Momentum relatif**, **suivi de tendance**, puis leur combinaison. Le breakout est une piste conditionnelle si une activité intraday est retenue. Qualité/valorisation et retour à la moyenne restent des recherches complémentaires.
- Les IQ peuvent rechercher, expliquer et proposer ; le code Python vérifie les critères et autorise ou refuse l'ordre. Un exemple où un agent IA trade directement ne satisfait pas automatiquement cette architecture.
- Le **garde-fou cash reste désactivé pour les recherches exploratoires actuelles**. Les déficits de cash et l'emprunt implicite doivent être signalés. Les modes actifs seront réévalués sur une stratégie pertinente, avec gestion correcte des refus et exécutions.
- Aucun ordre Paper/Live ni changement de code n'est autorisé par la seule mise à jour de ce document. Les commits GitHub restent à la charge de l'utilisateur.

Le [plan principal](plan_mini_fonds_lumibot.md) porte la numérotation des étapes ; la prochaine est **l'étape 3, phase B**. La [synthèse](synthese_audit_strategies_lumibot.md) résume l'inventaire et les réserves.

## 2. Ce que les tests précédents ont établi

L'étape 2 de la conversation est terminée avec réserves : Momentum original sur **SPY, VEU, AGG**, capital simulé de 100 000 USD, période 2021–2025, résultats reproductibles sur deux exécutions par fournisseur.

| Configuration | Yahoo | Alpaca | Interprétation |
|---|---:|---:|---|
| Momentum original, garde-fou désactivé | +19,53 % | +18,84 % | Référence sur ETF ; cash parfois négatif et dividendes non crédités au portefeuille. |
| Rejeu rapide, mode sans emprunt | −2,83 % | −2,72 % | Aucune trésorerie négative, mais nombreux refus que la stratégie ne gère pas correctement ; une exécution par source pour ce rejeu. |

Ces tests ne valident ni un portefeuille d'actions S&P 500, ni les quatre cycles intraday, ni une performance réalisable après tous les coûts. Le garde-fou empêche les ordres non financés ; il ne corrige pas les variables de position qu'une stratégie met à jour avant confirmation de l'achat.

Le garde-fou installé propose `disabled`, `cash` et `margin` avec plafond d'emprunt explicite. Son périmètre actuel est celui des ordres simples long-only actions/ETF en backtest. Il n'est pas un Risk Gate complet, un modèle de marge sur dérivés ou un contrôle Paper/Live. Le choix exploratoire `disabled` n'est pas une validation de l'emprunt ni une autorisation de reprendre ce réglage en exploitation.

## 3. Stratégies et composants réellement présents dans le dépôt

La présence d'un fichier n'est pas une preuve d'avantage de trading. La distinction Python / IA / composant doit apparaître dans chaque compte rendu.

| Priorité de recherche | Fichier ou composant | État réel | Travail nécessaire pour notre projet |
|---|---|---|---|
| 1 — Momentum relatif | `lumibot/example_strategies/stock_momentum.py` | Exemple Python : un seul actif parmi trois ETF par défaut, fenêtre de deux jours, réévaluation toutes les deux séances. | Variante distincte sur actions S&P 500 ; définir plusieurs positions, pondérations, horizons et fréquence ; ne pas considérer deux jours comme un réglage validé. |
| 2 — Suivi de tendance | `lumibot/example_strategies/ai_researcher_trader.py` ; `SMAIndicator` dans `lumibot/indicators/builtin.py` | Exemple IA sur un symbole, moyenne de 20 barres ; indicateur SMA disponible indépendamment. | Définir une règle mesurable par titre et/ou un filtre de marché ; distinguer signal de prix, interprétation IA et autorisation Python. |
| 3 — Combinaison Momentum + tendance | Assemblage des éléments précédents | Hypothèse de stratégie à construire et tester ; pas un mini-fonds prêt à l'emploi. | Comparer Momentum seul, tendance seule et combinaison ; isoler l'effet de chaque composant. |
| Conditionnel — Breakout d'ouverture | `lumibot/example_strategies/ai_opening_range_breakout.py` | Exemple IA : range 9h30–9h45 ET, contrôles horaires, univers comprenant ETF et actions. | Restreindre aux actions S&P 500, vérifier données intraday, règles d'entrée/sortie et gestion entre les quatre cycles. Les consignes de stop/sortie dans les prompts ne remplacent pas une qualification des ordres effectivement placés. |
| Ultérieur — Qualité/valorisation | `ai_trading_team_warren_buffett_value.py`, `ai_trading_team_bill_ackman_concentrated.py` dans `lumibot/example_strategies/` | Exemples IA, univers restreints et décisions guidées par prompts. | Définir les critères, les dates de publication et l'horizon ; ne pas assimiler les noms d'investisseurs à une validation de performance. |
| Ultérieur — Retour à la moyenne | `lumibot/example_strategies/ccxt_backtesting_example.py` | Exemple Python sur crypto et bandes de Bollinger ; pas une stratégie actions déjà qualifiée. | Adapter dans une variante dédiée aux actions ; fixer entrées, invalidations, coûts et comportement en tendance forte. |
| Outils complémentaires | `RSIIndicator`, `BollingerBandsIndicator`, `VWAPIndicator` | Indicateurs disponibles, pas des stratégies complètes. | Construire et tester des règles explicites ; éviter de multiplier les indicateurs sans hypothèse précise. |

`ai_vwap.py` utilise SPY par défaut et des agents IA ; il n'est pas une stratégie multi-actions S&P 500 prête à reprendre. `agent_macro_risk.py`, les rotations ETF et l'exemple Citadel sectoriel ne respectent pas notre périmètre s'ils sont copiés tels quels.

L'organisation `ai_trading_team_bull_bear_large_cap_stocks.py` (recherche, arguments favorables, objections, décision) peut inspirer le processus des IQ. Cette architecture n'est pas un signal économique et doit être évaluée séparément.

## 4. Fonctionnement des quatre activations

Les rôles suivants sont décidés comme base fonctionnelle ; les heures précises et la politique des demi-séances restent à valider avant exécution.

| Cycle | Recherche / contrôle | Action éventuelle |
|---|---|---|
| 1 — Avant ouverture | Actualités connues, annonces d'entreprise, état du marché, classement et positions existantes. | Préparer un plan ; ne pas supposer connus les prix d'ouverture ou la barre complète du jour. |
| 2 — Après ouverture | Vérifier les prix et conditions d'exécution effectivement disponibles, les signaux et ordres déjà ouverts. | Entrer, conserver, ajuster ou refuser selon les règles de la variante. |
| 3 — En cours de séance | Nouvelles informations, invalidations, expositions et rapprochement des exécutions. | Gérer les positions ou ne rien faire ; éviter les ordres dupliqués. |
| 4 — Avant clôture | Bilan des positions, ordres en attente, événements connus et hypothèses overnight. | Conserver ou sortir selon la stratégie ; aucune obligation de tout vendre pour une stratégie à horizon de plusieurs jours. |

Les décisions doivent être journalisées même en l'absence de transaction. Le calendrier est celui du marché, en **America/New_York**, avec jours fériés, changements d'heure et clôtures anticipées. L'exécution d'ordres de protection peut survenir entre deux activations ; quatre observations seules ne prouvent pas qu'un risque intraday est contrôlé.

**Compatibilité technique à établir :** `register_cron_callback` est explicitement ignoré en mode backtest dans cette installation. L'exemple `schedule_function.py` ne prouve donc pas les quatre activations historiques. Le protocole doit utiliser l'horloge simulée et une granularité appropriée. Un classement peut utiliser des barres journalières terminées, tandis que les quatre moments de décision/exécution nécessitent des observations adaptées ; ne pas simuler quatre cours différents avec une seule barre journalière.

## 5. Protocole de comparaison en phase B

### 5.1 Univers et données

1. Définir les membres historiques du S&P 500 et les règles d'entrée/sortie de l'univers.
2. Vérifier liquidité, identifiants, historique préalable, splits, dividendes et titres retirés. Un ticker actuel ne garantit pas la même société à toutes les dates.
3. Un prototype réduit peut être envisagé selon des règles établies à l'avance ; le nombre de titres suivis et le nombre de positions sont deux paramètres différents, encore à arbitrer.
4. Comparer les sources avec des hypothèses cohérentes : une différence de signal, d'ajustement ou de prix de valorisation n'est pas un effet de stratégie.
5. Documenter les trous de données et leurs conséquences ; ne pas fabriquer de prix ou masquer une période tronquée.

### 5.2 Variantes prioritaires

| ID | Variante | Question |
|---|---|---|
| A | Momentum relatif sur actions S&P 500, sans filtre | La sélection ajoute-t-elle une valeur après coûts et risque ? |
| B | Suivi de tendance sur les titres, à règles définies | La persistance d'une tendance constitue-t-elle une référence intéressante ? |
| C | Momentum + filtre de tendance du marché | Le filtre améliore-t-il le profil par rapport à A, en tenant compte des reprises manquées ? |
| D | Candidate retenue, avec exécution/dimensionnement adaptés puis garde-fou activé | La stratégie fonctionne-t-elle avec des contraintes de financement explicites et des refus correctement traités ? |
| E | Breakout d'ouverture sur actions, si l'intraday est retenu | L'opportunité persiste-t-elle avec les données, délais et coûts réalisables ? |

Les variantes qualité et retour à la moyenne feront l'objet de protocoles distincts ultérieurs. Aucun horizon, SMA, nombre de positions, seuil sectoriel ou fréquence de rééquilibrage n'est considéré optimisé par défaut. Tester une seule modification logique à la fois. Une comparaison hebdomadaire/mensuelle est une hypothèse possible pour des stratégies lentes, sans supprimer les quatre contrôles quotidiens.

### 5.3 Mesures et critères

Enregistrer rendement total et annualisé, drawdown, volatilité, Sharpe/Sortino avec leurs conventions, turnover, nombre d'ordres et d'exécutions, concentration, exposition, séances sans position, liquidités minimales et financement implicite. Ajouter le bilan de chaque cycle, les décisions `HOLD`, refus, annulations et exécutions partielles.

Comparer à une référence S&P 500/SPY correctement décrite. Le benchmark n'est pas une position négociée de notre portefeuille. Éviter de mélanger rendement de prix, dividendes crédités et cours ajustés ; intégrer les frictions selon les hypothèses réellement appliquées.

La période **2021–2025 a déjà été examinée** ; elle reste exploratoire. Définir avant l'ajustement les périodes de conception/validation et un test final réellement non consulté. Mesurer la robustesse sur plusieurs régimes et une sensibilité raisonnable aux paramètres. Ne pas sélectionner la variante au seul rendement le plus élevé.

## 6. Rôle des IQ et autorisation d'ordre

Les IQ analysent les informations disponibles et proposent `BUY`, `SELL` ou `HOLD`, avec motifs et preuves datées. Le Python confronte ces propositions aux règles de stratégie, à l'univers, aux données, aux positions et aux ordres en cours, puis produit `APPROVED`, `REJECTED` ou `REVIEW_REQUIRED`.

Seule une décision autorisée peut être convertie en ordre ; les deux autres interdisent un nouvel ordre. Les IQ ne peuvent pas modifier leurs limites ou contourner un rejet. Les exemples LumiBot à agent trader doivent être adaptés à cette architecture ; leur présence ne prouve pas qu'une validation déterministe des signaux est déjà construite.

La désactivation choisie du garde-fou cash pendant l'exploration est un paramètre explicite des simulations. Elle ne supprime pas l'objectif d'un Risk Gate complet pour une future exploitation et ne permet pas de décrire ces résultats comme des performances sans emprunt. Avant Paper, une candidate devra gérer les liquidités, positions, ordres ouverts, doublons, rejets, données périmées, exposition, limites sectorielles et arrêt d'urgence.

Journal : proposition de l'IQ → preuves et contrôles Python → décision → ordre demandé → réponse et exécutions broker. Une soumission ne doit jamais être enregistrée comme un achat réussi sans confirmation.

## 7. Sources et portée de la recherche

Sources consultées pour établir la base de recherche le 30 octobre 2026 :

- [S&P Dow Jones Indices — S&P 500](https://www.spglobal.com/spdji/en/indices/equity/sp-500/) : définition de l'univers de grandes entreprises américaines ; pas une preuve de rendement de notre sélection.
- [AQR — Fact, Fiction and Momentum Investing](https://www.aqr.com/Insights/Research/Journal-Article/Fact-Fiction-and-Momentum-Investing) : littérature sur le momentum relatif ; ne valide pas le réglage de deux jours ni le code de notre variante.
- [AQR — Implementing Momentum: What Have We Learned?](https://www.aqr.com/insights/research/working-paper/implementing-momentum-what-have-we-learned) : mise en œuvre et frictions à examiner.
- [Zarattini, Barbon et Aziz — A Profitable Day Trading Strategy for the U.S. Equity Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284) : recherche sur une variante ORB de cinq minutes et un univers américain plus large ; pas une validation du seul S&P 500 ou de notre exemple IA de quinze minutes.
- [de Groot, Huij et Zhou — Another look at trading costs and short-term reversal profits](https://repub.eur.nl/pub/25718) : sensibilité du retour à la moyenne aux coûts et à la construction du portefeuille.
- [Asness, Frazzini et Pedersen — Quality minus junk](https://link.springer.com/article/10.1007/s11142-018-9470-2) : facteur académique de qualité, notamment étudié en long-short ; pas une preuve de sélection rentable par agent IA « Buffett ».
- [QuantConnect — Research Guide](https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/research-guide) : biais d'anticipation et de survivance des univers historiques.
- [LumiBot — Agent Built-In Tools](https://lumibot.lumiwealth.com/agents_builtin_tools.html) et code local : distinguer agent de recherche et agent disposant d'outils d'ordre ; les exemples doivent être vérifiés dans la version installée.
- [Reddit / algotrading — Opening Range Breakout for Stocks in Play](https://www.reddit.com/r/algotrading/comments/1hezqql/opening_range_breakout_for_stocks_in_play_code/) : piste de discussion communautaire, sans validation indépendante de ses résultats.

Les études portent sur des implémentations, horizons, univers et coûts spécifiques. Elles fondent des hypothèses de recherche ; aucun rendement n'est transféré automatiquement à notre portefeuille.

## 8. Prochaine action

Préparer **l'étape 3 de la phase B du plan principal** : protocole d'univers S&P 500, couverture des données, quatre cycles simulés et paramètres restant à arbitrer. Ne pas commencer une adaptation de code ou une autre stratégie sans mandat explicite. Garder le mode cash-guard `disabled` pour les simulations exploratoires actuelles, avec ses réserves visibles.
