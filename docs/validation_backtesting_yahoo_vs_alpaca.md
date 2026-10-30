# Validation comparative des backtests LumiBot : Yahoo Finance vs Alpaca (2024)

**Date de l'évaluation :** 29 octobre 2026  
**Auteur :** Antigravity  
**Projet :** Mini-fonds d'investissement algorithmique (Windows 11, Python 3.13.5, LumiBot 4.6.33, Alpaca Paper Trading).  
**Statut global :** **VALIDÉ** (pour les deux sources, avec spécificités d'ajustement documentées).

---

## 1. Résumé exécutif

Cette étape (« Étape 1 bis ») a permis d'exécuter et de comparer deux backtests rigoureusement identiques sur l'intégralité de l'année boursière 2024 (du 1er janvier 2024 au 1er janvier 2025, soit 252 séances de cotation) sur l'actif de référence **SPY** avec un capital initial de **100 000,00 USD** selon la stratégie passive de référence `BuyAndHold`.

### Faits marquants :
1. **Les deux moteurs de données fonctionnent à 100 %** : `YahooDataBacktesting` et `AlpacaBacktesting` ont tous deux franchi l'ensemble du cycle de backtest sans erreur et sans blocage.
2. **Reproductibilité absolue** : Chaque test a été exécuté deux fois consécutives. Les résultats obtenus entre le Run 1 et le Run 2 pour chaque fournisseur sont strictement identiques au centime près.
3. **Explication de l'écart (+24,19 % vs +26,45 %)** : L'écart de performance provient du mode d'ajustement des dividendes :
   - **Yahoo Finance** dans sa configuration native LumiBot opère sur les cours de marché **non ajustés des dividendes** (*Raw Price Return*, prix d'achat initial à 472,16 $).
   - **Alpaca** dans sa configuration native LumiBot (`auto_adjust=True`, soit `adjustment="all"`) opère sur les cours **ajustés des dividendes et splits** (*Total Return*, prix d'achat initial rétro-ajusté à 457,18 $).
   - Lorsque Alpaca est configuré sans ajustement de dividende (`auto_adjust=False`), il achète à **472,16 $** (prix identique à Yahoo) et aboutit à une valeur finale de **124 844,19 $** (très proche des **124 187,57 $** de Yahoo).
4. **Intégrité broker** : Aucun ordre n'a été émis sur le compte Alpaca Paper Trading (0 ordre transmis, vérifié via l'API de trading).

---

## 2. Environnement et version LumiBot

- **Version LumiBot :** `4.6.33`
- **Branche Git :** `dev`
- **Commit Git :** `a5f0ee6d80e22d81f491611535b9eff6408fe159`
- **Interpréteur :** Python 3.13.5 (Windows 11 64-bit)
- **Configuration d'encodage active :** `PYTHONUTF8=1` et `PYTHONIOENCODING=utf-8`
- **État des clés API :** Clés Alpaca Paper actives dans le `.env` local, aucune clé exposée, placeholders Data Downloader commentés.

---

## 3. Configuration détaillée de chaque source

### Source A : Yahoo Finance (`YahooDataBacktesting`)
- **Adaptateur :** `lumibot.backtesting.YahooDataBacktesting` (hérite de `YahooData` via `yfinance`).
- **Nature du flux :** Données historiques journalières publiques (gratuit, sans clé API).
- **Mode d'ajustement natif :** `auto_adjust=False`. Les cours manipulés sont les cours réels négociés (*Open*, *High*, *Low*, *Close* non altérés par les dividendes futurs).
- **Remarque technique :** L'activation explicite de `auto_adjust=True` sous `YahooDataBacktesting` dans cette version de LumiBot provoque une anomalie de nommage de colonne (`'open'`), car le dataframe retourné par yfinance en mode ajusté n'est pas attendu sous cette forme par le cache YahooData. Il convient donc de laisser Yahoo en `auto_adjust=False`.

### Source B : Alpaca (`AlpacaBacktesting`)
- **Adaptateur :** `lumibot.backtesting.AlpacaBacktesting` (hérite de `DataSourceBacktesting` via `alpaca-py`).
- **Nature du flux :** **SIP Feed officiel** (Consolidated Tape des bourses américaines). Le volume moyen journalier de SPY constaté (~60 à 120 millions de titres par jour) confirme qu'il s'agit du flux consolidé US complet et non du sous-flux IEX (qui ne représente que ~2 millions de titres).
- **Mode d'ajustement natif :** `auto_adjust=True` (`adjustment="all"` dans `StockBarsRequest`). Les cours historiques sont ajustés à la fois pour les divisions d'actions (*splits*) et les dividendes réinvestis (*Total Return*).
- **Paramètre critique :** `full_window=True` doit être explicitement spécifié lors de l'appel pour que le backtest aille jusqu'à la date de fin demandée (sinon, en mode config explicite hérité, le moteur s'arrête 3 jours avant).

---

## 4. Commandes exactes pour reproduire les tests

Un script autonome a été créé dans le dépôt pour automatiser et pérenniser cette vérification comparative :  
📄 [scripts/validation_backtesting_yahoo_vs_alpaca.py](file:///c:/Users/cycli/Documents/GitHub/Limubot/scripts/validation_backtesting_yahoo_vs_alpaca.py)

### Commande globale (exécute les deux et affiche la synthèse) :
```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python scripts/validation_backtesting_yahoo_vs_alpaca.py
```

### Commande unitaire — Yahoo Finance (2024 complet) :
```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python -c "
from datetime import datetime
from lumibot.example_strategies.stock_buy_and_hold import BuyAndHold
from lumibot.backtesting import YahooDataBacktesting

results, strategy = BuyAndHold.run_backtest(
    datasource_class=YahooDataBacktesting,
    backtesting_start=datetime(2024, 1, 1),
    backtesting_end=datetime(2025, 1, 1),
    benchmark_asset='SPY',
    show_plot=False,
    save_tearsheet=False,
    show_progress_bar=False,
    parameters={'buy_symbol': 'SPY'}
)
print('Valeur finale Yahoo:', strategy.portfolio_value)
"
```

### Commande unitaire — Alpaca (2024 complet) :
```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python -c "
from datetime import datetime
import pytz
from lumibot.credentials import ALPACA_CONFIG
from lumibot.example_strategies.stock_buy_and_hold import BuyAndHold
from lumibot.backtesting import AlpacaBacktesting

tz = pytz.timezone('America/New_York')
results, strategy = BuyAndHold.run_backtest(
    datasource_class=AlpacaBacktesting,
    backtesting_start=tz.localize(datetime(2024, 1, 1)),
    backtesting_end=tz.localize(datetime(2025, 1, 1)),
    benchmark_asset='SPY',
    show_plot=False,
    save_tearsheet=False,
    show_progress_bar=False,
    parameters={'buy_symbol': 'SPY'},
    timestep='day',
    market='NYSE',
    config=ALPACA_CONFIG,
    auto_adjust=True,
    full_window=True
)
print('Valeur finale Alpaca:', strategy.portfolio_value)
"
```

---

## 5. Tableau comparatif complet

| Indicateur / Métrique | Yahoo Finance (`auto_adjust=False`) | Alpaca (`auto_adjust=True`, défaut) | Alpaca (`auto_adjust=False`, brut) | Écart Yahoo vs Alpaca (Défaut) |
| :--- | :---: | :---: | :---: | :---: |
| **Flux de données** | Yahoo Finance (yfinance) | Alpaca SIP Feed (Consolidated) | Alpaca SIP Feed (Consolidated) | Public vs Broker API |
| **Période couverte** | 02/01/2024 au 31/12/2024 | 02/01/2024 au 31/12/2024 | 02/01/2024 au 31/12/2024 | Identique |
| **Nombre de séances (barres)** | 252 barres | 252 barres | 252 barres | **0 (Parfait accord)** |
| **Ajustement dividende** | Non ajusté (*Price Return*) | Ajusté (*Total Return*) | Non ajusté (*Price Return*) | Conceptuel |
| **Prix d'achat initial (02/01)** | **472,16 $** | **457,18 $** | **472,16 $** | -14,98 $ (effet dividendes) |
| **Quantité achetée (100k$)** | 209 SPY | 218 SPY | 211 SPY | +9 actions |
| **Cash résiduel non alloué** | 1 318,56 $ | 334,76 $ | 374,24 $ | Différence d'arrondi entier |
| **Prix final (31/12)** | 587,89 $ | 578,51 $ | 589,90 $ | Différence d'ajustement |
| **Valeur finale portefeuille** | **124 187,57 $** | **126 449,94 $** | **124 844,19 $** | +2 262,37 $ (+1,82 %) |
| **Rendement total** | **+24,19 %** | **+26,45 %** | **+24,84 %** | +2,26 % |
| **Rendement annualisé (CAGR)** | **24,21 %** | **26,47 %** | **24,86 %** | +2,26 % |
| **Ratio de Sharpe** | **1,45** | **1,60** | **1,49** | +0,15 |
| **Ratio de Sortino** | **2,00** | **2,22** | **2,05** | +0,22 |
| **Max Drawdown** | **-9,00 %** | **-9,07 %** | **-9,07 %** | -0,07 % (quasi identique) |
| **Durée max Drawdown** | 43 jours | 43 jours | 43 jours | **0 jour (identique)** |
| **Volatilité annualisée** | 12,63 % | 12,57 % | 12,67 % | -0,06 % |
| **Durée d'exécution** | ~8,2 à 8,6 secondes | ~9,1 à 9,5 secondes | ~10,5 secondes | Très rapide dans les 2 cas |
| **Reproductibilité Run 1 vs 2** | **100 % stricte** | **100 % stricte** | **100 % stricte** | Aucune variance |

---

## 6. Analyse approfondie des écarts

### 1. Pourquoi le prix d'achat du 02/01/2024 est-il à 472,16 $ chez Yahoo et 457,18 $ chez Alpaca ?
Le 2 janvier 2024 à 09h30, le cours réel à l'ouverture de SPY était de **472,16 $**.
Au cours de l'année 2024, le fonds SPY a versé 4 dividendes trimestriels (mars, juin, septembre, décembre) totalisant environ 7,00 $ par part.
- **Alpaca (`auto_adjust=True`)** utilise la méthode standard de la finance académique (*CRSP Total Return*) : tous les cours passés sont multipliés par un facteur d'ajustement $< 1$ pour refléter la valeur capitalisée avec dividendes. Le cours d'ouverture devient ainsi $472,16 \times 0,96827 = \mathbf{457,18\ \$}$.
- **Yahoo (`auto_adjust=False`)** prend le cours d'ouverture brut de 472,16 $. Les dividendes ne sont pas automatiquement réinvestis dans le prix de l'action.
- **Preuve irréfutable :** Lorsque l'on passe Alpaca en `auto_adjust=False`, Alpaca achète au centime près à **472,16 $** !

### 2. Pourquoi la quantité d'actions varie-t-elle (209 vs 211 vs 218) ?
Dans la stratégie d'exemple `stock_buy_and_hold.py` :
`quantity = int(self.get_portfolio_value() // current_value)`
- Chez Alpaca ajusté : $100\,000 // 457,18 = \mathbf{218}$ actions.
- Chez Alpaca non ajusté : $100\,000 // 472,16 = \mathbf{211}$ actions ($99\,625,76\ \$$ investis).
- Chez Yahoo : Au moment précis de l'évaluation pré-ouverture à 09h30, `self.get_last_price("SPY")` retournait la cotation précédente de clôture (476,49 $), calculant $100\,000 // 476,49 = \mathbf{209}$ actions ($98\,681,44\ \$$ investis). Lors de l'exécution au marché à 472,16 $, les 209 actions ont été achetées, laissant 1 318,56 $ de cash non investi.

### 3. Concordance de la dynamique boursière
Malgré cet écart de dividende, la dynamique de marché est **absolument identique** :
- Même nombre de séances : 252 jours.
- Même plus haut et même date de fin.
- Même profil de baisse : **Drawdown max de 9,0 % chez les deux fournisseurs**, durant exactement **43 jours** dans les deux cas.
- Volatilité annualisée identique à 0,06 % près (12,63 % vs 12,57 %).

---

## 7. Chemins des artefacts générés

Tous les artefacts ont été générés et vérifiés dans le dossier `logs/` :

- **Rapports de transactions CSV :**
  - Yahoo Run 1 : `logs/BuyAndHold_2026-10-29_18-59_dCzVnh_trades.csv`
  - Yahoo Run 2 : `logs/BuyAndHold_2026-10-29_18-59_mz2Ry3_trades.csv`
  - Alpaca (Ajusté) Run 1 : `logs/BuyAndHold_2026-10-29_19-00_cEsobe_trades.csv`
  - Alpaca (Ajusté) Run 2 : `logs/BuyAndHold_2026-10-29_19-00_nTToH4_trades.csv`
  - Alpaca (Non ajusté) : `logs/BuyAndHold_2026-10-29_19-01_djj4qS_trades.csv`
- **Fichiers métriques JSON (QuantStats) :**
  - Yahoo : `logs/BuyAndHold_2026-10-29_18-59_mz2Ry3_tearsheet_metrics.json`
  - Alpaca : `logs/BuyAndHold_2026-10-29_19-00_nTToH4_tearsheet_metrics.json`
- **Fichiers Parquet :** `stats`, `trades`, `indicators`, `trade_events` générés pour chaque exécution.

---

## 8. Verdicts indépendants

### Verdict Yahoo Finance : **VALIDÉ**
- **Points forts :** Gratuit, instantané, ne consomme pas de quota d'API Alpaca, données complètes 2024.
- **Réserves / Précautions :** Doit être utilisé avec `auto_adjust=False`. Les dividendes ne sont donc pas capitalisés dans la variation du cours de l'action.

### Verdict Alpaca : **VALIDÉ**
- **Points forts :** Flux institutionnel consolidé (SIP), données historiques de haute précision issues directement de l'infrastructure de notre broker de paper trading, prise en charge native du *Total Return* (`auto_adjust=True`) ou des cours bruts (`auto_adjust=False`), mise en cache locale automatique dans `<LUMIBOT_CACHE_FOLDER>/alpaca/`.
- **Réserves / Précautions :** Nécessite une clé Alpaca valide dans `.env` et le paramètre `full_window=True`.

---

## 9. Recommandation pour les futurs backtests Momentum

Pour le développement de notre première stratégie Momentum sur panier d'ETFs (Étape 2) :

1. **Source Principale recommandée : `AlpacaBacktesting`**
   - **Pourquoi :** C'est le flux du broker que nous utiliserons ensuite en Paper Trading. Les calculs de rentabilité relative entre ETFs (`SPY`, `QQQ`, `TLT`, `GLD`, `SHV`) bénéficieront du mode `auto_adjust=True`, ce qui est indispensable pour comparer loyalement un ETF distribuant beaucoup de dividendes (comme `TLT` ou `SHV`) avec un ETF de croissance réinvestissant peu (comme `QQQ`).
2. **Source Secondaire de validation croisée : `YahooDataBacktesting`**
   - **Pourquoi :** Permet une contre-vérification rapide, indépendante et sans clé API, pour s'assurer qu'un signal ou une surperformance ne dépend pas d'une anomalie spécifique d'un seul fournisseur.

---
*Fin du rapport de validation comparative. Prêt pour l'étape 2 sur validation de l'utilisateur.*

