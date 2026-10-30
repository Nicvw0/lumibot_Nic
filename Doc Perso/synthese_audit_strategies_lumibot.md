# LumiBot — Synthèse actualisée et décisions du mini-fonds

État de référence pour poursuivre la mise au point sur actions individuelles du S&P 500.

**Dernière mise à jour :** 30 octobre 2026  
**Statut :** étape 2 terminée avec réserves ; prochaine étape : phase B, étape 3  
**Public :** propriétaire du projet et agents intervenant sur les recherches

## 1. Périmètre décidé

- **Actions individuelles du S&P 500**, marché américain. Utiliser l'appartenance à l'indice à la date simulée. Pas de portefeuille d'ETF dans cette première version ; SPY reste possible comme benchmark ou indicateur.
- **Quatre activations par séance normale** : avant ouverture, après ouverture, en cours de séance et avant clôture. Les heures exactes et les règles des séances écourtées restent à définir.
- Chaque activation peut analyser, confirmer, agir ou ne rien faire. Quatre activations ne forcent ni quatre achats ni quatre rééquilibrages. Des positions peuvent être conservées plusieurs jours.
- Backtesting d'abord, puis Alpaca Paper après validation. Aucun ordre Paper/Live autorisé par ces documents ; aucune modification de code implicitement déclenchée par le plan.
- IQ pour les recherches/propositions, Python pour la vérification des critères et l'autorisation finale d'ordre.
- **Garde-fou cash désactivé pour les recherches exploratoires**, avec cash négatif et emprunt implicite signalés. Réévaluation des modes actifs lorsqu'une stratégie pertinente sera trouvée ; gestion des refus et dimensionnement à traiter avant une comparaison opérationnelle.

Le [plan principal](plan_mini_fonds_lumibot.md) contient la numérotation de référence. Le [document des stratégies](strategies_trading_mini_fonds_lumibot.md) détaille les hypothèses, sources et critères.

## 2. Historique validé et réserves

L'audit initial Antigravity concernait LumiBot 4.6.33, commit `a5f0ee6d`, Python 3.13.5 et Windows. Cette référence historique n'est pas le dernier commit des modifications locales installées ; aucun nouveau hash de commit n'est affirmé ici.

- [x] Audit et configuration du backtesting effectués.
- [x] Référence Buy & Hold et comparaison des sources examinées.
- [x] **Étape 2 de la conversation : Momentum original sur SPY/VEU/AGG, 2021–2025, capital simulé 100 000 USD, deux exécutions reproductibles par fournisseur.** Sans protection : +19,53 % Yahoo / +18,84 % Alpaca ; SPY séparé : +83,65 % / +82,95 %.
- [x] Garde-fou à trois modes construit, installé par l'utilisateur et vérifié dans le dépôt : `disabled`, `cash`, `margin` avec plafond explicite.
- [x] Rejeu rapide avec mode sans emprunt : −2,83 % Yahoo / −2,72 % Alpaca, aucun cash négatif, mais nombreux refus non correctement gérés par les variables internes de Momentum. Ce rejeu comprend une exécution par source, pas une nouvelle preuve de reproductibilité du mode actif.

**Limites des chiffres :** les positions de ce test étaient des ETF ; il ne valide pas le futur portefeuille d'actions S&P 500. Cash parfois négatif sans intérêts modélisés dans le test sans protection ; dividendes non crédités au portefeuille ; conventions de signaux et prix différentes entre Yahoo et Alpaca. La période 2021–2025 est déjà consultée et ne constitue pas un test final vierge.

Les rapports de preuve ont été produits dans la conversation (`rapport_final_etape_2.md`, `rapport_comparatif.md`). Ils ne sont pas supposés déjà présents dans ce dossier du dépôt. L'ancien [audit détaillé](../docs/audit_strategies_lumibot.md) doit être lu comme un historique, avec cette mise à jour.

## 3. Candidats réellement disponibles dans LumiBot

| Ordre de recherche | Candidat / source locale | Statut exact pour notre projet |
|---|---|---|
| 1 | Momentum relatif — `lumibot/example_strategies/stock_momentum.py` | Exemple Python disponible ; adaptation requise vers plusieurs actions S&P 500, pondérations et horizons à définir. Deux jours n'est pas un réglage validé. |
| 2 | Tendance — `ai_researcher_trader.py` ; `SMAIndicator` | Exemple IA sur un symbole et composant SMA disponible ; règle et construction du portefeuille à préciser. |
| 3 | Momentum avec filtre de tendance | Combinaison à construire et comparer, pas un mini-fonds déjà livré. |
| Si intraday retenu | Breakout — `ai_opening_range_breakout.py` | Exemple IA, range de quinze minutes et cadence horaire ; données intraday et adaptation des cycles/univers nécessaires. |
| Ultérieur | Qualité/valorisation — `ai_trading_team_warren_buffett_value.py`, `ai_trading_team_bill_ackman_concentrated.py` | Exemples IA, pas des facteurs quantitatifs validés ; données financières datées et horizon à définir. |
| Ultérieur | Retour à la moyenne — `ccxt_backtesting_example.py` | Exemple crypto à bandes de Bollinger, à adapter ; pas une stratégie actions prête à exécuter. |
| Architecture complémentaire | `ai_trading_team_bull_bear_large_cap_stocks.py` | Recherche → arguments favorables → objections → décision ; ce flux d'agents n'est pas à lui seul un avantage économique démontré. |

Les fichiers abrégés de ce tableau appartiennent à `lumibot/example_strategies/`. Les indicateurs se trouvent dans `lumibot/indicators/builtin.py`. Les références et limites de la recherche sont détaillées dans le document des stratégies.

## 4. Composants transversaux et vérifications

- **Planification :** `schedule_function.py` montre `register_cron_callback`, mais cette méthode est **ignorée en backtest** dans cette installation. Il faut prouver les quatre cycles avec l'horloge simulée, les données adéquates et le calendrier America/New_York ; ne pas déclarer le problème résolu par le seul exemple cron.
- **Ordres/protection :** `stock_bracket.py`, `stock_limit_and_trailing_stops.py` et le rééquilibrage sont des composants d'exécution ; leur compatibilité avec une candidate reste à tester. Le garde-fou actuel en mode actif ne couvre pas les brackets ou dérivés.
- **Garde-fou installé :** [CASH_GUARD.md](../docs/CASH_GUARD.md). Périmètre : ordres simples long-only actions/ETF en backtest, réservations et contrôle au prix d'exécution. Il ne protège pas Paper/Live ni tous les événements de trésorerie. Il est distinct du Risk Gate complet restant à construire.
- **Modes :** `disabled` pour l'exploration actuelle ; `cash` sans emprunt ; `margin` avec montant d'emprunt explicite. Aucun mode actif n'est choisi automatiquement par la mise à jour de ces documents.
- **Suivi des ordres :** positions basées sur les exécutions confirmées ; différencier refus, attente, annulation et exécution partielle. Ne pas considérer une soumission comme un achat réussi.
- **Données :** membres historiques S&P 500, titres retirés et changements de ticker ; historique préalable réel ; absence de données futures ; dividendes/splits/coûts décrits. Des barres journalières ne prouvent pas quatre exécutions intraday.
- **Qualification :** 59 tests hors ligne du correctif cash réussis ; deux tests existants de rapports dépendant du réseau ont échoué aussi sur la version non modifiée. Ces chiffres ne certifient ni toute la suite LumiBot ni les brokers connectés.

## 5. Suite du travail

1. **Phase B, étape 3 :** protocole S&P 500, qualité et granularité des données, quatre activations et horaires à arbitrer.
2. **Étapes 4–6 :** référence Momentum actions, tendance puis combinaison ; une modification logique par expérience.
3. **Phase C :** robustesse, test final indépendant, sélection d'une candidate, gestion d'exécution et réévaluation du garde-fou ; Risk Gate Python avant exploitation.
4. **Phase D :** historisation, interface, qualification des contrôles connectés puis observation en Paper.
5. **Phase E :** breakout conditionnel, retour à la moyenne, qualité/valorisation, agents complémentaires et hébergement selon les décisions futures.

**À ne plus reprendre comme objectif actif :** l'ancien panier d'ETF, une étape 2 encore déclarée bloquée, ou quatre cycles repoussés à une fonctionnalité optionnelle tardive. Les ETF des tests antérieurs restent uniquement une référence historique.

L'utilisateur réalise lui-même les commits et envois GitHub. Aucun commit, push, déploiement, lancement d'agent facturé ou ordre de trading n'est déclenché par ces documents.
