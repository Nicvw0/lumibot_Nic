# Rapport d'audit du dépôt LumiBot — Réutilisation des stratégies et composants

**Date de l'audit :** 29 octobre 2026  
**Auteur :** Antigravity  
**Projet cible :** Mini-fonds d'actions algorithmique (LumiBot + Alpaca Paper Trading)  
**Règle appliquée :** Audit strict en lecture seule, aucune modification du code source existant, aucun ordre réel.

---

## 1. Environnement et version inspectés

- **Dépôt Git local :** `c:\Users\cycli\Documents\GitHub\Limubot`
- **Branche active :** `dev` (suivi de `origin/dev`, dépôt distant `https://github.com/Nicvw0/lumibot_Nic.git`)
- **Commit Git :** `a5f0ee6d80e22d81f491611535b9eff6408fe159`
- **Version LumiBot :** `4.6.33` (vérifiée via `lumibot.__version__`)
- **Interpréteur Python :** Python 3.13.5 (Windows 11 64-bit, chemin : `C:\Users\cycli\AppData\Local\Programs\Python\Python313\python.exe`)
- **Statut des dépendances :** Toutes les dépendances de `requirements.txt` sont installées et satisfaites.
- **Connexion Alpaca Paper Trading :**
  - Statut : **Opérationnel et vérifié**
  - Compte : `AccountStatus.ACTIVE`
  - Devise : `USD`
  - Cash disponible : `10 000,00 $`
  - Pouvoir d'achat (*Buying power*) : `40 000,00 $`
  - Flux de données de marché en direct : Accessible (test de récupération du dernier prix sur `SPY` validé).

---

## 2. Inventaire et classification des stratégies et composants

### Tableau de synthèse

| Catégorie fonctionnelle | Fichier source exact | Classe / Composant | Classification | Résumé du fonctionnement |
| :--- | :--- | :--- | :---: | :--- |
| **1. Momentum relatif** | `lumibot/example_strategies/stock_momentum.py` | `Momentum` | **B** | Classement par performance passée (`Bars.get_momentum()`) sur une liste de symboles. Achète le premier. |
| **1. Momentum relatif (IA)** | `lumibot/example_strategies/agent_momentum_allocator.py` | `MomentumAllocatorStrategy` | **B** | Agent LLM qui évalue la tendance et l'actualité de TQQQ vs SHV (Treasury). |
| **1. Calcul de momentum** | `lumibot/entities/bars.py` | `Bars.get_momentum()` | **C** | Méthode native calculant `(close[-1] / close[-n-1]) - 1` ajusté des dividendes. |
| **2. Filtre de tendance** | `lumibot/indicators/builtin.py` | `SMAIndicator` | **C** | Indicateur SMA Pine v6 en temps constant O(1). Pas de stratégie complète dédiée. |
| **2. Filtre de tendance (IA)**| `lumibot/example_strategies/agent_macro_risk.py` | `MacroRiskStrategy` | **B** | Agent LLM qui arbitre TQQQ ou SHV selon la tendance de TQQQ et SPY. |
| **3. Breakout (IA)** | `lumibot/example_strategies/ai_opening_range_breakout.py` | `AIOpeningRangeBreakoutStrategy` | **B** | Détection du range 9h30-9h45 et achat sur cassure avec stop au plus bas du range. |
| **3. Breakout (Composant)**| `lumibot/example_indicators/donchian_midline.py` | `DonchianMidline` | **C** | Calcul des bornes haute et basse sur N périodes (Canaux de Donchian / Tortues). |
| **4. Mean Reversion** | `lumibot/example_strategies/ccxt_backtesting_example.py` | `CcxtBacktestingExampleStrategy` | **B** | Stratégie complète basée sur les Bandes de Bollinger (`%B < -0.13` achat, `%B > 1.2` vente). |
| **4. Indicateurs Mean Reversion**| `lumibot/indicators/builtin.py` | `BollingerBandsIndicator`, `RSIIndicator` | **C** | Implémentations natives des Bandes de Bollinger et du RSI. |
| **5. Allocation Multi-Agents IA**| `lumibot/example_strategies/ai_trading_team_ray_dalio_idea_meritocracy.py` | `AITradingTeamRayDalioIdeaMeritocracyStrategy` | **B** | Débat multi-agents (croissance, inflation) avec règle d'intégrité `ORDER_READINESS_RULE`. |
| **5. Actualités Alpaca (IA)**| `lumibot/example_strategies/agent_alpaca_news_builtin.py` | `AlpacaNewsBuiltinStrategy` | **B** | Analyse du flux d'actualités Alpaca News pour arbitrer SPY/QQQ vs SHV. |
| **6. Gestion du risque (Rééquilibrage)**| `lumibot/example_strategies/drift_rebalancer.py` + `lumibot/components/drift_rebalancer_logic.py` | `DriftRebalancer`, `DriftRebalancerLogic` | **A** | Rééquilibrage robuste selon dérive relative/absolue par rapport à des poids cibles. Vente avant achat. |
| **6. Gestion du risque (Ordres)**| `lumibot/example_strategies/stock_bracket.py` | `StockBracket` | **A** | Ordres Bracket natifs (`OrderClass.BRACKET`) avec Stop-Loss et Take-Profit simultanés. |
| **6. Gestion du risque (Ordres)**| `lumibot/example_strategies/stock_limit_and_trailing_stops.py` | `LimitAndTrailingStop` | **A** | Ordres stop suiveur (*trailing stop*) en pourcentage et en montant. |
| **6. Ordonnancement temporel**| `lumibot/example_strategies/schedule_function.py` | `ScheduledFunctionStrategy` | **A** | Utilisation de `register_cron_callback` pour déclencher des fonctions à heures fixes. |
| **7. Backtesting Alpaca** | `lumibot/backtesting/alpaca_backtesting.py` | `AlpacaBacktesting` | **A** | Moteur de backtest utilisant l'API historique d'Alpaca avec benchmark automatique (`SPY`). |
| **7. Backtesting Yahoo** | `lumibot/backtesting/yahoo_backtesting.py` | `YahooDataBacktesting` | **A** | Moteur de backtest gratuit basé sur Yahoo Finance avec génération de tearsheet QuantStats. |

---

## 3. Analyse détaillée des stratégies et composants

### 3.1 Momentum relatif

#### Fichier 1 : `lumibot/example_strategies/stock_momentum.py` (Classe `Momentum`) — **Catégorie B**
- **Logique d'entrée et de sortie :**
  - Récupère l'historique de prix sur une liste de symboles (`self.symbols`) sur `self.period` jours via `self.get_bars()`.
  - Calcule la rentabilité de chaque actif via `bars_set.get_momentum(num_periods=self.period)`.
  - Sélectionne l'actif ayant la meilleure rentabilité relative.
  - Si l'actif sélectionné est différent de l'actif détenu, il vend la totalité de la position existante puis achète le nouvel actif avec 100 % de la valeur du portefeuille (`self.get_portfolio_value() // best_asset_price`).
- **Actifs et fréquence :** Univers par défaut `["SPY", "VEU", "AGG"]`, fréquence journalière (`self.await_market_to_close()`).
- **Paramètres modifiables :** `self.period` (nombre de jours de calcul, par défaut 2), `self.symbols` (univers d'actifs).
- **Données nécessaires :** Flux de prix journalier (Yahoo Finance ou Alpaca).
- **Backtesting :** Oui, nativement configuré avec `YahooDataBacktesting` et benchmark `SPY`.
- **Compatibilité Alpaca Paper :** Directe via le bloc `Alpaca(ALPACA_CONFIG)`.
- **Limites et adaptations requises :**
  - **Concentration extrême (100 % sur 1 seul actif) :** Non adapté à un fonds diversifié. Il faut adapter la sélection pour retenir le Top $N$ actions (ex. 3 à 5 actions) avec une pondération plafonnée (ex. 20 % maximum par titre).
  - **Absence de filtre de rentabilité absolue :** La stratégie achète le "meilleur" actif même si sa rentabilité est fortement négative (en marché baissier).
  - **Exécution séquentielle sans validation :** L'ordre de vente est soumis immédiatement avant l'ordre d'achat sans attendre la confirmation du fill (`wait_for_order_execution()`), ce qui peut provoquer un rejet pour insuffisance de cash.

#### Fichier 2 : `lumibot/entities/bars.py` (Méthode `Bars.get_momentum`) — **Catégorie C**
- Implémente le calcul vectorisé du momentum :
  ```python
  close_values = underlying_df['close'].to_numpy()
  momentum = (close_values[-1] / close_values[-num_periods-1]) - 1
  ```
- Composant réutilisable directement dans n'importe quelle stratégie LumiBot.

---

### 3.2 Filtre de tendance de marché

#### Fichier : `lumibot/indicators/builtin.py` (Classe `SMAIndicator`) — **Catégorie C**
- **Logique :** Moyenne mobile simple (*Simple Moving Average*) conforme aux spécifications Pine Script v6, avec état glissant en temps constant $\mathcal{O}(1)$.
- **Constat d'audit :** Il n'existe pas dans le dépôt de stratégie autonome prête à l'emploi intitulée "TrendFilter" ou "200_SMA_Filter".
- **Composants disponibles :**
  Dans n'importe quelle stratégie LumiBot, interroger la tendance de SPY se fait nativement en 2 lignes de code :
  ```python
  spy_bars = self.get_bars("SPY", 200, timestep="day")
  sma_200 = spy_bars.pandas_df['close'].mean()
  current_spy = self.get_last_price("SPY")
  is_bullish = current_spy > sma_200
  ```
- **Adaptation requise :** Intégrer cette condition comme règle préalable (*Trend Gate*) avant toute allocation momentum : si `is_bullish` est faux, le fonds n'ouvre aucune nouvelle position longue et se réfugie en liquidités ou sur un ETF monétaire ultra-court (`SHV` ou `BIL`).

---

### 3.3 Cassure de prix (*Breakout*)

#### Fichier : `lumibot/example_strategies/ai_opening_range_breakout.py` — **Catégorie B**
- **Logique :** Stratégie en deux temps. À partir de 10h00, un agent "chercheur" mesure le range 9h30-9h45 sur un univers d'actions tech (`AAPL`, `MSFT`, `NVDA`, etc.). Un agent "trader" achète la première action qui franchit son plus haut, avec un stop sous le plus bas du range (risque max 1 % du compte) et un ratio de gain de 1.5. Clôture de toutes les positions avant la fermeture du marché.
- **Limites :** Repose entièrement sur des invites LLM (*prompts*). Pour notre mini-fonds, une règle déterministe en Python pur est requise pour éliminer l'aléa et les coûts d'inférence.

#### Fichier : `lumibot/example_indicators/donchian_midline.py` — **Catégorie C**
- **Logique :** Calcule la borne supérieure (plus haut sur $N$ périodes) et inférieure (plus bas sur $N$ périodes) via un deque.
- **Réutilisabilité :** Composant idéal pour implémenter une cassure déterministe (type canaux de Donchian / Tortues) sans faire appel à un LLM.

---

### 3.4 Retour à la moyenne (*Mean Reversion*)

#### Fichier : `lumibot/example_strategies/ccxt_backtesting_example.py` — **Catégorie B**
- **Logique :**
  - Calcule les Bandes de Bollinger (`bbu`, `bbm`, `bbl`) et l'indicateur `%B` (`bbp = (close - bbl) / (bbu - bbl)`).
  - Signal d'achat à contre-tendance : quand `%B < -0.13` (survente prononcée en dehors des bandes) et allocation de `cash_at_risk = 0.25` (25 % du cash).
  - Signal de sortie / vente : quand `%B > 1.2` (surachat au-dessus de la bande haute).
- **Adaptation requise :** Le code est écrit pour des paires crypto CCXT, mais la formule mathématique et les appels de l'API LumiBot (`create_order`, `get_cash`, `get_historical_prices`) sont 100 % identiques pour des actions américaines (`Asset(symbol='SPY', asset_type='stock')`).

---

### 3.5 Stratégies avec Agents IA et actualités

#### Fichier 1 : `lumibot/example_strategies/agent_alpaca_news_builtin.py` — **Catégorie B**
- **Logique :** Lit le flux d'actualités financières via l'outil natif Alpaca News (`alpaca_news`). Si le sentiment global est positif sur les indices, achète `SPY` ou `QQQ` ; si négatif, achète `SHV`.
- **Règle de sécurité observée :** Intègre la restriction temporelle `Use only news published before now` pour prévenir le biais de regard vers le futur (*look-ahead bias*).

#### Fichier 2 : `lumibot/example_strategies/ai_trading_team_ray_dalio_idea_meritocracy.py` — **Catégorie B**
- **Logique :** Équipe multi-agents reproduisant la méritocratie d'idées de Bridgewater. Deux agents recherchent les arguments (croissance vs inflation) à partir de données macroéconomiques FRED et Alpaca News.
- **Composant fondamental découvert : `ORDER_READINESS_RULE`**
  ```python
  "Immediately before every buy or sell order, call account_portfolio, "
  "account_positions, and market_last_price for the exact ordered symbol... "
  "LumiBot rejects blind orders with ORDER_READINESS_REQUIRED."
  ```
  Ce mécanisme natif de LumiBot impose de vérifier l'état du compte et du marché avant toute émission d'ordre.

---

### 3.6 Gestion du risque et exécution d'ordres

#### Fichier 1 : `lumibot/example_strategies/drift_rebalancer.py` et `lumibot/components/drift_rebalancer_logic.py` — **Catégorie A**
- **Logique :** Reçoit une liste d'actifs avec des poids cibles (`portfolio_weights`). Calcule l'écart (*drift*) réel par rapport à la cible. Déclenche un rééquilibrage si la dérive dépasse un seuil (`drift_threshold`, ex. 5 %).
- **Sécurité d'exécution :**
  - **Séquençage Vente puis Achat :** Vend d'abord les actifs excédentaires pour libérer du cash, attend `fill_sleeptime` secondes, puis soumet les ordres d'achat.
  - **Protection contre le slippage :** Paramètre `acceptable_slippage` (ex. 0,5 %).
  - **Choix du type d'ordre :** Supporte `OrderType.MARKET` et `OrderType.LIMIT`.
- **Verdict :** **C'est le composant le plus abouti et le plus sécurisé du dépôt pour gérer un portefeuille multi-actifs.**

#### Fichier 2 : `lumibot/example_strategies/stock_bracket.py` — **Catégorie A**
- **Logique :** Émet un ordre d'achat couplé à deux ordres enfants : un `secondary_limit_price` (prise de profit) et un `secondary_stop_price` (stop de protection du capital).
- **Compatibilité Alpaca :** Alpaca supporte nativement les ordres Bracket au niveau serveur. Si le stop est touché chez Alpaca, l'ordre de profit est annulé automatiquement sans latence locale.

#### Fichier 3 : `lumibot/example_strategies/schedule_function.py` — **Catégorie A**
- **Logique :** Utilise `self.register_cron_callback("minute hour * * *", callback)` pour planifier des tâches à des heures précises de la journée (ex. analyse pré-marché à 9h00, vérification à 10h00, 12h00, 14h00, clôture à 15h45).
- **Verdict :** Répond exactement au besoin du plan du mini-fonds (4 points de contrôle journaliers).

---

## 4. Résultats des tests exécutés et anomalies identifiées

### 4.1 Tests unitaires existants (Pytest)
Les suites de tests représentatives du cœur de LumiBot ont été exécutées avec succès :
- `tests/test_strategy_parameters.py` : **7/7 passés (100 %)**
- `tests/test_strategy_methods.py` : **19/19 passés (100 %)**
- `tests/test_agent_indicator_numeric_contracts.py` : **17/17 passés (100 %)**

### 4.2 Anomalies et pièges découverts lors des tests réels

1. **Bug d'encodage de la barre de progression sous Windows (`cp1252`) :**
   - **Constat :** Lors d'un backtest, la fonction `print_progress_bar` dans `lumibot/tools/helpers.py` (ligne 752) écrit le caractère de bloc plein `█` (`\u2588`). Sous l'invite de commande Windows par défaut, cela déclenche une erreur fatale :  
     `UnicodeEncodeError: 'charmap' codec can't encode character '\u2588'`.
   - **Solution testée et validée :** Définir systématiquement les variables d'environnement suivantes dans les scripts d'exécution :
     ```powershell
     $env:PYTHONUTF8 = "1"
     $env:PYTHONIOENCODING = "utf-8"
     ```

2. **Blocage réseau lié aux variables factices du Data Downloader :**
   - **Constat :** Dans le `.env` copié depuis `.env.local.example`, les variables suivantes étaient renseignées avec des valeurs d'exemple :
     ```env
     DATADOWNLOADER_BASE_URL=https://<your-downloader-host>:8080
     DATADOWNLOADER_API_KEY=REPLACE_ME
     BACKTESTING_DATA_SOURCE='{"default":"thetadata", ...}'
     ```
   - LumiBot détecte ces variables au démarrage et tente d'acheminer les requêtes de données historiques vers ce serveur distant inexistant. Cela provoque un gel complet (*hang*) des backtests sur des délais d'attente réseau infinis.
   - **Solution impérative :** Pour utiliser Yahoo Finance ou l'API Alpaca en direct, il faut commenter ou supprimer ces variables du `.env`.

3. **Absence de contrôleur de risque pré-ordre dans LumiBot :**
   - **Constat :** La méthode interne `_validate_order` dans `lumibot/strategies/strategy.py` ne vérifie que :
     - Si l'ordre n'est pas `None` ;
     - S'il s'agit d'une instance de la classe `Order` ;
     - Si la quantité n'est pas nulle.
   - Elle ne vérifie **aucun** plafond d'exposition par titre, aucun ratio de levier global, aucune fraîcheur temporelle des barres, et ne dispose d'aucun mécanisme natif de *Kill Switch* automatique en cas de drawdown intraday excessif.

---

## 5. Plan de réutilisation recommandé pour le mini-fonds

Pour construire la première version testable du mini-fonds avec le maximum de composants éprouvés et le minimum de code à écrire, voici la feuille de route :

```
[Univers d'actifs liquides : 10 ETFs sectoriels ou actions SP500]
                           │
                           ▼
  [Étape 1 : Filtre de tendance SPY > 200 SMA]
        │                               │
    (Si FAUX)                       (Si VRAI)
        │                               │
        ▼                               ▼
  [100% Cash ou SHV/BIL]     [Étape 2 : Classement Momentum Relatif]
                             (Bars.get_momentum sur 6 mois, top 3-4 actifs)
                                        │
                                        ▼
                             [Étape 3 : Allocation & Drift Rebalancer]
                             (Poids cibles : 25% max par actif, calcul drift)
                                        │
                                        ▼
                             [Étape 4 : Risk Gate Déterministe Python]
                             (Kill switch, taille max, cash tampon 5%)
                                        │
                                        ▼
                             [Étape 5 : Exécution Alpaca Paper Trading]
                             (Ordres Bracket ou Vente puis Achat)
```

### Éléments existants à reprendre directement :
1. **Moteur d'itération et calcul du momentum :**  
   Reprendre la structure de `lumibot/example_strategies/stock_momentum.py` et `Bars.get_momentum()`.
2. **Logique de dimensionnement et de rééquilibrage du portefeuille :**  
   Reprendre `DriftRebalancerLogic` (`lumibot/components/drift_rebalancer_logic.py`) pour diviser le capital de façon égale entre les $N$ meilleurs actifs et séquencer les ventes avant les achats.
3. **Planification des 4 rendez-vous journaliers :**  
   Reprendre `register_cron_callback` de `lumibot/example_strategies/schedule_function.py`.
4. **Moteur de backtest et benchmark :**  
   Utiliser `AlpacaBacktesting` ou `YahooDataBacktesting` avec `benchmark_asset="SPY"`.

### Éléments manquants à développer (la "Risk Gate" Python) :
Développer une classe légère `RiskManager` intégrée à la stratégie qui intercepte chaque ordre avant soumission :
- **Plafond unitaire :** Rejeter tout ordre dont la valeur dépasse 25 % du portefeuille net.
- **Plafond de levier :** Rejeter tout ordre si `valeur_positions + ordre > 0.95 * portfolio_value` (conserver au moins 5 % de cash libre).
- **Anti-doublon :** Vérifier `self.get_tracked_orders()` pour interdire un ordre sur un symbole ayant déjà un ordre en attente.
- **Kill Switch automatique :** Interrompre la stratégie et liquider les positions (`self.sell_all()`) si la baisse journalière du portefeuille dépasse un seuil critique (ex. 3 %).

---

## 6. Recommandation finale

1. **Point de départ recommandé :**
   Prendre la logique de **`lumibot/example_strategies/stock_momentum.py`** comme colonne vertébrale, en y injectant le module de gestion de portefeuille de **`lumibot/example_strategies/drift_rebalancer.py`**.

2. **Paramètres initiaux à tester :**
   - **Univers :** 6 à 8 ETFs liquides non corrélés (ex. `SPY`, `QQQ`, `IWM`, `GLD`, `TLT`, `VNQ`, `SHV`).
   - **Période de calcul du momentum :** 60 à 120 jours de bourse (au lieu des 2 jours de l'exemple initial).
   - **Filtre de marché :** Moyenne mobile 200 jours sur `SPY` (allocation en `SHV` ou cash si `SPY < SMA 200`).
   - **Nombre d'actifs retenus :** Les 3 meilleurs actifs, alloués à 30 % chacun (+ 10 % cash de sécurité).
   - **Fréquence de rééquilibrage :** Hebdomadaire ou mensuelle (pour éviter le sur-trading et les frais).

3. **Ce qu'il ne faut PAS faire :**
   - Ne pas utiliser d'agent IA pour l'émission directe des ordres.
   - Ne pas lancer de backtest tant que les variables d'environnement factices `DATADOWNLOADER_*` sont actives dans le `.env`.
   - Ne pas exécuter de stratégie sans la variable `PYTHONUTF8=1` sous Windows.

---
*Fin du rapport d'audit. Aucune modification du code source n'a été effectuée.*

