#!/bin/bash

# Veille financière matinale — Bibi
# Exécuté automatiquement lun-ven à 7h00

CLAUDE_BIN="/Users/hanser/.local/bin/claude"
TELEGRAM_TOKEN="8776626703:AAFRMM2Jz5gjD4Vfmi4FIZG-x7QYSV5p9D0"
CHAT_ID="718679715"
LOG_FILE="/Users/hanser/Desktop/jarvis-starter-kit/scripts/veille.log"

echo "$(date): Démarrage veille financière" >> "$LOG_FILE"

PROMPT='Tu es Bibi, le Jarvis personnel de Clément Hanser.

Ta mission : effectuer une veille financière matinale complète et envoyer un message Telegram.

Étape 1 — Recherche avec WebSearch et WebFetch :
- Levées de fonds du jour (France, Europe, US si significatives) : TechCrunch, Maddyness, Les Echos Start, Sifted, Crunchbase
- Actu financière Europe : résultats entreprises, macro BCE/Fed, marchés. Sources : Les Echos, Reuters, BFM Business
- Clôture Wall Street la nuit dernière (S&P 500, Nasdaq, Dow Jones) + actualités notables US
- IPO récentes ou à venir sur NYSE/Nasdaq cette semaine
- Cours Bitcoin : appelle https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true via curl

Étape 2 — Formate le message (max 4000 caractères) :

🌅 *Bonjour Clément — Veille du [DATE]*

💰 *LEVÉES DE FONDS*
• [Startup] — [Montant] ([Série]) — [secteur] — [contexte]

📊 *ACTU FINANCIÈRE EUROPE*
• [titre] — [1-2 lignes]

🇺🇸 *MARCHÉS US — NUIT*
• Clôture : S&P 500 [val] ([var]), Nasdaq [val] ([var]), Dow [val] ([var])
• [actualité notable]

🚀 *IPO US*
• [Société] — [marché] — [date] — [secteur] — [1 ligne]

₿ *BITCOIN*
Prix : [val $]
Variation 24h : [%]

📈 *MARCHÉS EUROPE*
CAC 40 : [val] ([var])
Euro/Dollar : [val]
OAT 10 ans : [val]

_Bonne journée 🎯_

Étape 3 — Envoie le message via cette commande curl exacte (remplace MESSAGE par le texte) :
curl -s -X POST "https://api.telegram.org/bot'"$TELEGRAM_TOKEN"'/sendMessage" -d chat_id='"$CHAT_ID"' -d parse_mode=Markdown --data-urlencode "text=MESSAGE"

Si une donnée est indisponible, indique-le brièvement. Ne fabrique rien.'

# Appel Claude avec accès aux outils web
"$CLAUDE_BIN" -p "$PROMPT" --allowedTools "WebSearch,WebFetch,Bash" >> "$LOG_FILE" 2>&1

echo "$(date): Veille terminée" >> "$LOG_FILE"
