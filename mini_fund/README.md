# Architecture personnelle du mini-fonds
Structure vide réutilisant les points d’entrée de LumiBot.
Last Updated : 2026-10-30
Status : Squelette uniquement, non exécutable en trading.
Audience : Propriétaire et développeurs du mini-fonds.

## Overview

Ce dossier appartient au projet personnel, hors du cœur `lumibot/`.
Aucune stratégie concrète, aucun agent, ordre, collecte S&P 500, horaire ou
règle financière n’est implémenté.

## Structure

- `strategies/` : catalogue vide et base abstraite héritant de LumiBot Strategy.
- `phases/` : quatre points d’entrée métier non implémentés.
- `common/` : noms des phases et contrat de contexte.
- `agents/` : emplacement des futurs rôles, avec le gestionnaire natif.
- `universe/` : emplacement pour la future acquisition et admissibilité.
- `execution/` : emplacement des futurs contrôles avant exécution native.
- `config/application.json` : stratégie active, horaires et source non définis.
- `runners/` : points de raccordement distincts live/backtest, bloqués explicitement.
- `runtime/` : emplacement des futurs états et résultats isolés.
- `ui/index.html` : structure web statique, sans connexion ni commande.
- `__main__.py` : inspection en lecture seule, sans importer LumiBot.

Depuis la racine du dépôt :

```powershell
python -m mini_fund
```

Pour prévisualiser la structure web, ouvrir `ui/index.html` dans un navigateur.
Cette page est statique ; ce n’est pas encore une interface de suivi.

## Réutilisation vérifiée

LumiBot 4.6.33 fournit Strategy, le cycle de séance, l’horloge simulée,
le calendrier, les agents, la mémoire, les brokers, les ordres et le backtest.
Les fichiers de phase n’introduisent aucun moteur concurrent.
Trader.run_all exige une stratégie par lancement et refuse le mélange
backtest/live. Cette limite ne garantit pas l’exclusivité entre processus.
register_cron_callback est ignoré en backtest.

Sources locales examinées : `lumibot/strategies/strategy.py`,
`lumibot/traders/trader.py`, `lumibot/components/agents/manager.py`,
`docsrc/agents_flows.rst`, `docsrc/strategy_api_overview.rst`.
Aucune interface locale prête à l’emploi identifiée dans les sources examinées.
Les rapports HTML de LumiBot restent à réutiliser lors du raccordement du suivi.

## Raccordements ultérieurs

Ajouter séparément : acquisition S&P 500, règles de contrôle, horaires et
prévention des doublons, stratégies, agents éventuels, isolation des versions,
persistance configurée, verrou par compte et lancement paper/live.
Les emplacements réservés ne sont pas des protections actives.
Aucun lancement réel n’est autorisé par la création de cette structure.

## Déclencheurs de phase — raccordement ajouté

La base abstraite possède maintenant `configure_phase_triggers()` et les appels
aux déclencheurs depuis les événements natifs avant ouverture, début de séance,
itération, avant clôture et après clôture. Une future stratégie appelle la
configuration depuis son `initialize()`, et fournit uniquement ses tâches via
`run_phase()`. Aucun exemple concret de stratégie n’est ajouté.

`common/triggers.py` ne crée ni thread ni ordonnanceur. La boucle LumiBot appelle
les contrôles ; le temps vient de `get_datetime()` et le calendrier de
`lumibot.tools.helpers.get_trading_days`. Les jours sans marché sont ignorés et
la clôture réelle de la séance sert de référence, y compris à 13 h.

`phase_times` configure les horaires validés de New York : 9 h 00, 10 h 15,
12 h 45 et 15 h 30. Les règles sont ouverture −30 min, ouverture +45 min,
milieu de séance et clôture −30 min. L’ancre `midpoint` calcule le milieu réel.
Pour une clôture à 13 h : 9 h 00, 10 h 15, 11 h 15 et 12 h 30.
Les jours sans séance sont ignorés. Une valeur nulle désactive un moment.

`triggers.poll_seconds` vaut 1, cadence demandée sans garantie à la seconde.
`max_lateness_seconds` vaut 60, tolérance technique initiale ajustable.
Au-delà, le moment est `missed`, sans rattrapage. Un échec est `failed` et
n’est pas réessayé automatiquement. Aucun processus n’est lancé par le fichier
de configuration ; aucune stratégie concrète n’est enregistrée.

Les événements sont journalisés en UTC avec la date de séance de New York,
l’heure cible et le retard observé. Le registre par jour et phase est conservé
dans `self.vars.mini_fund_phase_runs` ; son état `running` est posé avant la tâche
pour empêcher un double appel dans le processus. Une entrée restaurée n’est pas
relancée automatiquement. La durabilité après redémarrage dépend du backend de
sauvegarde LumiBot effectivement configuré : ce composant n’est ni un verrou
entre processus ni une garantie d’exécution exactement une fois après panne.

Les tâches restent synchrones : une tâche longue peut retarder les suivantes.
La cadence réelle dépend des événements et des données du moteur ; les backtests
sur barres journalières ne valident pas les quatre moments intrajournaliers.
Aucun processus permanent n’est lancé par cette mise à jour, aucun lanceur n’est
raccordé et aucune tâche métier n’est implémentée.

Vérifications hors ligne :

```powershell
python -B -m unittest mini_fund.checks.test_triggers mini_fund.checks.test_native_triggers -v
```

Les heures dans ces tests sont des fixtures, pas les horaires retenus du fonds.
Les tests natifs neutralisent le chargement des fichiers d’identifiants et ne
construisent aucun broker ni compte. Ils vérifient les points d’entrée et le
calendrier réel LumiBot, pas un lancement live ou un backtest complet.