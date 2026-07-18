import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const defaultInput = resolve(scriptDir, "../normalized/reviews-master.jsonl");
const defaultOutput = resolve(scriptDir, "../qa/consumer-theme-candidates.jsonl");

export const consumerCandidateRules = [
  { id: "role.cross-generation-grandchild", dimension: "role", label: "cross_generation_family", pattern: /\b(granddaughter|grandson|grandchild|grandkids?)\b/i },
  { id: "role.immediate-family", dimension: "role", label: "family_members", pattern: /\b(family|wife|husband|daughter|son|mom|mother|dad|father|parents?|in-laws?)\b/i },
  { id: "role.friends-guests", dimension: "role", label: "friends_or_guests", pattern: /\b(friends?|guests?|everyone|coworkers?|co-workers?)\b/i },

  { id: "scene.party-gathering", dimension: "scene", label: "party_or_gathering", pattern: /\b(party|parties|gatherings?|get-together|celebration)\b/i },
  { id: "scene.birthday", dimension: "scene", label: "birthday", pattern: /\b(birthday|b-day)\b/i },
  { id: "scene.gift-occasion", dimension: "scene", label: "gift_occasion", pattern: /\b(gift|present|christmas|holiday)\b/i },
  { id: "scene.home-karaoke", dimension: "scene", label: "home_karaoke", pattern: /\b(home karaoke|karaoke night|family night|friends? over for karaoke|at home)\b/i },
  { id: "scene.travel-outdoor", dimension: "scene", label: "travel_or_outdoor", pattern: /\b(travel|road trip|camping|outdoors?|outside|backyard|beach|tailgate)\b/i },

  { id: "job.sing-along", dimension: "job", label: "shared_singing", pattern: /\b(sing along|sang together|sing together|duets?)\b/i },
  { id: "job.two-mics", dimension: "job", label: "shared_singing", pattern: /\b(two|2|both)\s+(wireless\s+|rechargeable\s+)?(microphones?|mics?)\b/i },
  { id: "job.quick-start", dimension: "job", label: "quick_start", pattern: /\b(easy to (use|set up|setup)|right out of the box|plug and play|ready to use|user[- ]friendly)\b/i },
  { id: "job.bring-karaoke-home", dimension: "job", label: "bring_karaoke_home", pattern: /\b(karaoke bar closed|home karaoke|friends? over for karaoke|karaoke at home)\b/i },
  { id: "job.take-it-along", dimension: "job", label: "portable_entertainment", pattern: /\b(bring it|take it|travel|friends?'? houses?|easy to carry|take anywhere)\b/i },

  { id: "motivation.explicit-two-mic-choice", dimension: "motivation", label: "explicit_two_mic_choice", pattern: /\b(glad|happy)\s+i\s+(chose|got)\b.{0,90}\b(two|2)\s+(microphones?|mics?)\b/i },
  { id: "motivation.gift-purchase", dimension: "motivation", label: "gift_purchase", pattern: /\b(bought|purchased|got|getting|is)\b.{0,40}\b(gift|present)\s+(for|to)\b/i },
  { id: "motivation.venue-replacement", dimension: "motivation", label: "replace_external_venue", pattern: /\b(karaoke bar closed|bar closed down|instead of going to.*karaoke)\b/i },
  { id: "motivation.recommendation", dimension: "motivation", label: "recommendation_trigger", pattern: /\b(recommended|recommendation|told me about|suggested)\b/i },
  { id: "motivation.replace-upgrade", dimension: "motivation", label: "replace_or_upgrade", pattern: /\b(replace|replacement|upgrade|old karaoke|previous karaoke|another karaoke machine)\b/i },

  { id: "outcome.shared-joy", dimension: "outcome", label: "shared_fun_and_connection", pattern: /\b(had a blast|so much fun|lots of fun|fun and joy|laughing|made memories|family loves it|everyone loves it)\b/i },
  { id: "outcome.easy-start", dimension: "outcome", label: "low_setup_effort", pattern: /\b(easy to (use|set up|setup)|right out of the box|simple to get going|plug and play)\b/i },
  { id: "outcome.portable-flexibility", dimension: "outcome", label: "portable_flexibility", pattern: /\b(portable|compact|easy to carry|take anywhere|bring it on travel)\b/i },
  { id: "outcome.sound-performance", dimension: "outcome", label: "sound_and_atmosphere", pattern: /\b(sound (is|was|quality is) (amazing|awesome|great|excellent|incredible)|gets? loud|fills? the room|party atmosphere)\b/i },

  { id: "unmet.software-slow-buggy", dimension: "unmet_need", label: "software_performance", pattern: /\b(app|tablet|software|touch ?screen)\b.{0,80}\b(slow|buggy|freeze|freezes|frozen|laggy|doesn['’]?t recognize|unresponsive|crash)\b/i },
  { id: "unmet.battery-dead-charge", dimension: "unmet_need", label: "battery_reliability", pattern: /\b(battery|charge|charging|charger)\b.{0,90}\b(dead|not charging|won['’]?t charge|doesn['’]?t charge|bad|defect|only works? (when )?plugged|take it off it['’]?s dead)\b/i },
  { id: "unmet.mic-connect-charge", dimension: "unmet_need", label: "microphone_reliability", pattern: /\b(microphones?|mics?)\b.{0,100}\b(not work|stopped working|doesn['’]?t work|won['’]?t work|not connect|disconnect|delay|lag|not charging|won['’]?t charge)\b/i },
  { id: "unmet.content-subscription", dimension: "unmet_need", label: "content_service_transparency", pattern: /\b(subscription|monthly fee|have to pay|extra charge|not free|limited songs?|song selection)\b/i },
  { id: "unmet.tv-hdmi", dimension: "unmet_need", label: "tv_connection_expectation", pattern: /\b(tv|television|hdmi)\b.{0,100}\b(no sound|audio|delay|lag|doesn['’]?t work|won['’]?t work|only video)\b/i },
  { id: "unmet.setup-support", dimension: "unmet_need", label: "setup_and_support", pattern: /\b(instructions?|manual|support|customer service|set up|setup|pairing)\b.{0,90}\b(missing|unclear|confusing|difficult|hard|no response|never responded|can['’]?t figure)\b/i },
];

export function loadMasterReviews(pathOrUrl = defaultInput) {
  return readFileSync(pathOrUrl, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map(line => JSON.parse(line));
}

function extractMatchedText(text, match) {
  const start = Math.max(0, match.index - 70);
  const end = Math.min(text.length, match.index + match[0].length + 110);
  return text.slice(start, end).replace(/\s+/g, " ").trim();
}

export function discoverConsumerCandidates(reviews, rules = consumerCandidateRules) {
  const candidates = new Map();

  for (const review of reviews.filter(row => row && row.analysis_eligible !== false)) {
    const text = `${review.title_original || ""}\n${review.body_original || ""}`.trim();
    for (const rule of rules) {
      const match = text.match(rule.pattern);
      if (!match) continue;

      const key = `${review.review_id}|${rule.dimension}|${rule.label}`;
      const existing = candidates.get(key);
      if (existing) {
        if (!existing.rule_ids.includes(rule.id)) existing.rule_ids.push(rule.id);
        continue;
      }

      candidates.set(key, {
        review_id: review.review_id,
        dimension: rule.dimension,
        candidate_label: rule.label,
        rule_ids: [rule.id],
        matched_text: extractMatchedText(text, match),
        review_status: "pending",
        evidence_type: "unknown",
        decision_basis: null,
      });
    }
  }

  return [...candidates.values()]
    .map(row => ({ ...row, rule_ids: [...row.rule_ids].sort() }))
    .sort((a, b) => `${a.dimension}|${a.candidate_label}|${a.review_id}`.localeCompare(`${b.dimension}|${b.candidate_label}|${b.review_id}`));
}

function readArg(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? resolve(process.argv[index + 1]) : fallback;
}

if (resolve(process.argv[1] || "") === fileURLToPath(import.meta.url)) {
  const input = readArg("--input", defaultInput);
  const output = readArg("--output", defaultOutput);
  const candidates = discoverConsumerCandidates(loadMasterReviews(input));
  writeFileSync(output, `${candidates.map(row => JSON.stringify(row)).join("\n")}\n`, "utf8");
  console.log(JSON.stringify({ input, output, reviews: loadMasterReviews(input).length, candidates: candidates.length }));
}
