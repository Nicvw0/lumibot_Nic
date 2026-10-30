# LumiBot — Synthèse de l’audit et stratégies à tester

**Source :** synthèse du rapport communiqué par l’agent Antigravity (audit du dépôt local).  
**Environnement audité :** LumiBot 4.6.33, commit `a5f0ee6d` (branche `dev`), Python 3.13.5, Windows 11.  
**Objectif :** réutiliser les stratégies et composants du dépôt avant d’écrire du nouveau code. **Backtests puis Alpaca Paper Trading uniquement.**

## 1. Stratégies candidates

| Priorité | Stratégie | Source LumiBot identifiée | État selon l’audit | Adaptation / test envisagé |
|---|---|---|---|---|
| **1 — Démarrage** | **Momentum relatif** | `lumibot/example_strategies/stock_momentum.py` | **B : adaptation requise** | Passer de 100 % sur un actif à une sélection Top N d’ETF ; comparer fenêtres 60/90/120 jours et Top 1/3/5. |
| **2 — Variante du momentum** | **Filtre de tendance SPY / SMA 200** | `lumibot/indicators/builtin.py` (`SMAIndicator`) | **C : composant disponible** | Comparer momentum seul vs momentum avec filtre ; tester cash ou ETF défensif lorsque SPY est sous sa SMA 200. |
| **3 — Stratégie distincte** | **Breakout** | `ai_opening_range_breakout.py`, `donchian_midline.py` | **B/C : exemple IA / composant** | Étudier une version déterministe sur ETF/actions ; définir précisément entrée, sortie et horizon. |
| **4 — Stratégie distincte** | **Mean reversion** | `ccxt_backtesting_example.py` | **B : adaptation requise** | Adapter les bandes de Bollinger de la crypto vers les actions/ETF ; vérifier les données et les règles de sortie. |
| **Plus tard** | **Agents IA** | `agent_alpaca_news_builtin.py`, `ai_trading_team_ray_dalio_idea_meritocracy.py` | **B : exemples disponibles** | Tester leur valeur ajoutée *après* une référence déterministe ; aucun ordre IA sans validation Python. |

**A/B/C :** A = réutilisable presque tel quel ; B = adaptation nécessaire ; C = composants disponibles mais stratégie à assembler. Les classifications reflètent le rapport de l’agent, pas une validation indépendante.

## 2. Composants transversaux à réutiliser

- **Rééquilibrage / poids cibles :** `drift_rebalancer.py` et `DriftRebalancerLogic` ; vérifier leur intégration avant usage.
- **Ordres de protection :** `stock_bracket.py` (stop-loss / take-profit) ; pertinence à évaluer selon la stratégie.
- **Planification :** `schedule_function.py` et `register_cron_callback`.
- **Backtests / benchmarks :** `alpaca_backtesting.py`, `yahoo_backtesting.py` ; comparaison à SPY et rapports QuantStats selon configuration.
- **Risk Gate à développer :** contrôle Python indépendant avant ordre : exposition et levier, cash disponible, données fraîches, doublons, kill switch, journalisation. La validation native `_validate_order` est insuffisante selon l’audit.

## 3. Première expérience proposée : momentum ETF

**Univers initial suggéré par l’agent :** SPY, QQQ, IWM, GLD, TLT, VNQ, SHV (à vérifier selon disponibilité et historique). Ces ETF ne sont **pas tous décorrélés**.

**Hypothèses à tester, non paramètres optimisés :**
- Momentum sur **60 / 90 / 120 jours** ; sélection **Top 1 / 3 / 5**.
- Avec ou sans **filtre SPY > SMA 200**.
- Rééquilibrage à fréquence définie ; plafond indicatif **30 % par ligne**, tampon de cash **10 %** (cohérence à vérifier avec Top N).
- Comparer à **SPY buy-and-hold**, en tenant compte des frais, du slippage, du drawdown, du turnover et des périodes hors échantillon.

## 4. Blocages et vérifications avant développement

1. **Backtest complet non validé :** plusieurs essais interrompus / bloqués ; ne pas conclure que le moteur est opérationnel sur cette seule base.
2. **Console Windows :** utiliser `PYTHONUTF8=1` et `PYTHONIOENCODING=utf-8` pour éviter l’erreur d’encodage `cp1252` signalée.
3. **`.env` :** vérifier les valeurs factices `DATADOWNLOADER_BASE_URL` et `BACKTESTING_DATA_SOURCE` qui ont provoqué des blocages ; les corriger sans exposer les clés API.
4. **Tests unitaires :** 43/43 réussis selon l’agent ; cela ne remplace pas un backtest de bout en bout.
5. **Alpaca :** compte Paper Trading déclaré actif et prix SPY accessible ; **ne pas activer de trading réel**.

## 5. Ordre de travail recommandé

- [ ] **Étape 0 :** faire aboutir un backtest d’un exemple LumiBot inchangé, avec rapport de performance.
- [ ] **Étape 1 :** backtester le momentum existant comme référence.
- [ ] **Étape 2 :** tester Top N ETF et les fenêtres de momentum, sans changer plusieurs paramètres simultanément.
- [ ] **Étape 3 :** comparer avec/sans filtre SMA 200 et règles de rééquilibrage.
- [ ] **Étape 4 :** ajouter et tester le Risk Gate déterministe ; vérifier les refus d’ordres.
- [ ] **Étape 5 :** tester séparément Breakout puis Mean Reversion ; comparer sur les mêmes périodes et hypothèses de coûts.
- [ ] **Étape 6 :** envisager les agents IA seulement après validation des stratégies déterministes et passage prolongé en paper trading.

**Principe directeur :** réutiliser le code du dépôt, modifier le minimum, mesurer chaque changement, puis décider sur des résultats robustes — jamais sur un seul backtest favorable.
