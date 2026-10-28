// Authored storyline structure for the Reveal tab. Progress is not stored here:
// the page marks each node from the save export (bossCatalog flags and the
// questCatalog step states). `boss` matches a bossCatalog name exactly;
// `patterns` match lower-case fragments of questCatalog step descriptions.
window.ER_STORYLINES = {
  main: {
    title: "Main story · the Elden Throne",
    intro: "Two Great Runes open Leyndell. After the Fire Giant, the road runs through Farum Azula to the Ashen Capital and the final choice of ending.",
    stages: [
      {title: "Limgrave · Stormveil Castle", places: ["Limgrave", "Stormveil Castle"], nodes: [
        {label: "Margit, the Fell Omen", boss: "Margit, the Fell Omen"},
        {label: "Godrick the Grafted", boss: "Godrick the Grafted", rewards: ["Godrick's Great Rune", "Remembrance of the Grafted"]}]},
      {title: "Shardbearers · any two Great Runes open Leyndell", parallel: true, nodes: [
        {label: "Rennala, Queen of the Full Moon", boss: "Rennala, Queen of the Full Moon", note: "Liurnia · unlocks Rebirth", rewards: ["Great Rune of the Unborn", "Remembrance of the Full Moon Queen"]},
        {label: "Starscourge Radahn", boss: "Starscourge Radahn", note: "Caelid · the falling star opens Nokron", rewards: ["Radahn's Great Rune", "Remembrance of the Starscourge"]},
        {label: "Rykard, Lord of Blasphemy", boss: "Rykard, Lord of Blasphemy", note: "Volcano Manor", rewards: ["Rykard's Great Rune", "Remembrance of the Blasphemous"]}]},
      {title: "Leyndell, Royal Capital", places: ["Leyndell, Royal Capital"], nodes: [
        {label: "Godfrey, First Elden Lord (golden shade)", boss: "Godfrey, First Elden Lord"},
        {label: "Morgott, the Omen King", boss: "Morgott, the Omen King", rewards: ["Morgott's Great Rune", "Remembrance of the Omen King"]}]},
      {title: "Forbidden Lands · Mountaintops of the Giants", places: ["Forbidden Lands", "Mountaintops of the Giants"], nodes: [
        {label: "Melina hands over the Rold Medallion at the Erdtree thorns", item: "Rold Medallion", quest: "Melina", patterns: ["giving you the \"rold medallion\""], rewards: ["Rold Medallion"]},
        {label: "Fire Giant", boss: "Fire Giant", rewards: ["Remembrance of the Fire Giant"]},
        {label: "Forge of the Giants: Melina burns the Erdtree", note: "If you accepted the Flame of Frenzy, Melina has left and you light the forge yourself."}]},
      {title: "Crumbling Farum Azula", places: ["Crumbling Farum Azula"], nodes: [
        {label: "Godskin Duo", boss: "Godskin Duo", rewards: ["Smithing-Stone Miner's Bell Bearing [4]"]},
        {label: "Maliketh, the Black Blade", boss: "Maliketh, the Black Blade", rewards: ["Remembrance of the Black Blade"], note: "Leyndell becomes the Ashen Capital."}]},
      {title: "Leyndell, Ashen Capital · Elden Throne", places: ["Leyndell, Ashen Capital", "Elden Throne"], nodes: [
        {label: "Sir Gideon Ofnir, the All-Knowing", boss: "Sir Gideon Ofnir, the All-Knowing"},
        {label: "Hoarah Loux, Warrior", boss: "Hoarah Loux, Warrior"},
        {label: "Radagon of the Golden Order → Elden Beast", boss: "Elden Beast", rewards: ["Elden Remembrance"], note: "One continuous fight; no Site of Grace between the two phases."}]}
    ],
    optional: [
      {label: "Mohg, Lord of Blood", boss: "Mohg, Lord of Blood", note: "Mohgwyn Palace · via White Mask Varre's Pureblood Knight's Medal or the Consecrated Snowfield waygate", rewards: ["Mohg's Great Rune", "Remembrance of the Blood Lord"]},
      {label: "Malenia, Blade of Miquella", boss: "Malenia, Blade of Miquella", note: "Miquella's Haligtree · needs both Haligtree Secret Medallion halves (Albus, and Castle Sol after Commander Niall)", rewards: ["Malenia's Great Rune", "Remembrance of the Rot Goddess"]},
      {label: "Dragonlord Placidusax", boss: "Dragonlord Placidusax", note: "Crumbling Farum Azula · also where Miquella's Needle removes the Flame of Frenzy", rewards: ["Remembrance of the Dragonlord"]},
      {label: "Lichdragon Fortissax", boss: "Lichdragon Fortissax", note: "Fia's dream in Deeproot Depths", rewards: ["Remembrance of the Lichdragon"]}
    ],
    endings: {
      decision: "After the Elden Beast, the ending depends on what you carry and whose sign you answer. “Requirement met” means the save shows the item or step each ending needs.",
      doneLabel: "requirement met",
      options: [
        {label: "Age of Fracture", outcome: "Touch the Elden Ring with no Mending Rune selected. Always available.", rewards: ["Ending achievement"]},
        {label: "Age of Stars", outcome: "Finish Ranni's quest, then use her summon sign after the final fight.", quest: "Ranni the Witch", patterns: ["receiving the \"dark moon ring\""], rewards: ["Dark Moon Greatsword", "Ending achievement"]},
        {label: "Age of Order", outcome: "Follow Brother Corhyn and Goldmask to the Mending Rune of Perfect Order.", quest: "Brother Corhyn", patterns: ["receiving \"mending rune of perfect order\""], rewards: ["Mending Rune of Perfect Order"]},
        {label: "Age of the Duskborn", outcome: "Finish Fia's quest in Deeproot Depths for the Mending Rune of the Death-Prince.", quest: "Fia", patterns: ["receiving \"mending rune of the death-prince\""], rewards: ["Mending Rune of the Death-Prince"]},
        {label: "Blessing of Despair", outcome: "Use the Seedbed Curses on Dung Eater for the Mending Rune of the Fell Curse.", quest: "Dung Eater", patterns: ["receiving \"mending rune of the fell curse\""], rewards: ["Mending Rune of the Fell Curse"]},
        {label: "Lord of Frenzied Flame", outcome: "Accept the Flame of Frenzy from the Three Fingers beneath Leyndell. Melina leaves; Miquella's Needle can undo it before the end.", quest: "Hyetta", patterns: ["looting her body, receiving \"frenzied flame seal\""], rewards: ["Frenzied Flame Seal", "Ending achievement"]}
      ]
    }
  },
  forks: {
    "Millicent": [{
      decision: "Haligtree Drainage Channel: two summon signs, one choice.",
      options: [
        {label: "Aid Millicent", outcome: "Invade alongside her against her sisters.", patterns: ["choosing yes on aiding her"], rewards: ["Rotten Winged Sword Insignia"]},
        {label: "Challenge Millicent", outcome: "Duel her in her world.", patterns: ["choosing yes on challenging her"], rewards: ["Millicent's Prosthesis"]}
      ],
      after: "Either way she dies; return the Unalloyed Gold Needle to Malenia's flower.",
      afterRewards: ["Unalloyed Gold Needle", "Miquella's Needle", "Somber Ancient Dragon Smithing Stone"]
    }],
    "Sorceress Sellen": [{
      decision: "Raya Lucaria Grand Library: answer Sellen's sign or Jerren's invasion sign.",
      options: [
        {label: "Side with Sellen", outcome: "Help her defeat Jerren.", patterns: ["defeating jerren, receiving his amor"], rewards: ["Jerren's armor", "Glintstone Kris"]},
        {label: "Side with Jerren", outcome: "Defeat Sellen; Jerren rewards you outside.", quest: "Jerren", patterns: ["defeating sellen, receiving her bell bearing"], rewards: ["Sellen's Bell Bearing", "Witch's Glintstone Crown", "Ancient Dragon Smithing Stone"]}
      ]
    }],
    "Jerren": [{
      decision: "Raya Lucaria Grand Library: the same choice seen from Jerren's side.",
      options: [
        {label: "Side with Jerren", outcome: "Defeat Sellen in her world.", patterns: ["defeating sellen, receiving her bell bearing"], rewards: ["Sellen's Bell Bearing", "Witch's Glintstone Crown", "Ancient Dragon Smithing Stone"]},
        {label: "Side with Sellen", outcome: "Fight Jerren as her summon.", quest: "Sorceress Sellen", patterns: ["defeating jerren, receiving his amor"], rewards: ["Jerren's armor", "Glintstone Kris"]}
      ]
    }],
    "Dung Eater": [{
      decision: "After freeing him from the Sewer-Gaol, decide how his story ends.",
      options: [
        {label: "Use the Seedbed Curses", outcome: "Use the curses on him in the sewers; he dies and leaves the Mending Rune.", patterns: ["receiving \"mending rune of the fell curse\""], rewards: ["Mending Rune of the Fell Curse"]},
        {label: "Fight him", outcome: "Defeat him when he invades.", patterns: ["killing him and receiving \"sword of milos\""], rewards: ["Sword of Milos"]}
      ]
    }],
    "Nepheli Loux": [{
      decision: "After Godrick: hand Nepheli The Stormhawk King ash to make her ruler of Stormveil.",
      options: [
        {label: "Give The Stormhawk King", outcome: "Nepheli takes the throne; she rewards you there.", patterns: ["giving her \"the stormhawk king\" ash"], rewards: ["Ancient Dragon Smithing Stone"]},
        {label: "Seluvis's Potion route", outcome: "Part of Seluvis's puppet scheme; his quest decides the outcome.", quest: "Seluvis", patterns: ["accepting and receiving \"seluvis's potion\""], rewards: ["Seluvis's Potion"]}
      ]
    }],
    "Ranni the Witch": [{
      decision: "Ranni's Rise: enter her service or refuse.",
      options: [
        {label: "Enter her service", outcome: "Opens the Fingerslayer Blade, Nokron, Nokstella and Lake of Rot route.", patterns: ["choosing to enter her service"], rewards: ["Carian Inverted Statue", "Cursemark of Death", "Dark Moon Ring"]},
        {label: "Refuse", outcome: "Her quest pauses until you return and accept.", patterns: ["choosing to refuse to enter her service"], rewards: []}
      ],
      after: "Do not give Seluvis's Amber Draught to Ranni: it makes her quest impossible to finish.",
      afterRewards: ["Dark Moon Greatsword"]
    }],
    "Seluvis": [{
      decision: "Seluvis's scheme: whether to give Ranni the Amber Draught.",
      options: [
        {label: "Give Ranni the Draught", outcome: "Ranni's quest can no longer be finished, and Seluvis dies at his Rise.", patterns: ["giving ranni the draught"], rewards: ["Seluvis's Bell Bearing"]},
        {label: "Keep it", outcome: "Ranni's quest stays open; you still keep his earlier rewards.", patterns: ["receiving \"magic scorpion charm\""], rewards: ["Magic Scorpion Charm", "Amber Draught"]}
      ]
    }],
    "Fia": [{
      decision: "Roundtable Hold: give Fia the Cursemark of Death from Ranni's quest.",
      options: [
        {label: "Give the Cursemark", outcome: "Fia leaves for Deeproot Depths; enter her dream to fight Lichdragon Fortissax.", patterns: ["choosing \"give cursemark of death\""], rewards: ["Radiant Baldachin's Blessing", "Mending Rune of the Death-Prince"]},
        {label: "Keep it", outcome: "Her quest pauses at the Roundtable.", patterns: [], rewards: []}
      ]
    }],
    "Hyetta": [{
      decision: "Feed Hyetta Shabriri Grapes and the Fingerprint Grape, then choose whether to take the Flame of Frenzy.",
      options: [
        {label: "Accept the Flame of Frenzy", outcome: "Opens the Lord of Frenzied Flame ending; Melina leaves you.", patterns: ["looting her body, receiving \"frenzied flame seal\""], rewards: ["Frenzied Flame Seal", "Frenzyflame Stone"]},
        {label: "Refuse it", outcome: "Keeps Melina and every other ending open.", patterns: [], rewards: []}
      ]
    }],
    "Brother Corhyn": [{
      decision: "Tell Corhyn where Goldmask is, give him the Golden Order Principia, then cast Law of Regression at Leyndell's statue.",
      options: [
        {label: "Finish Goldmask's proof", outcome: "Goldmask leaves the Mending Rune of Perfect Order in the Ashen Capital; Corhyn dies afterwards.", patterns: ["receiving \"mending rune of perfect order\""], rewards: ["Golden Order Totality", "Mending Rune of Perfect Order", "Corhyn's Bell Bearing"]},
        {label: "Stop at prayerbooks", outcome: "Keep Corhyn alive as a vendor at the Roundtable or outside the Colosseum.", patterns: [], rewards: []}
      ]
    }],
    "White Mask Varre": [{
      decision: "Varre offers a Bloody Finger route to Mohgwyn Palace.",
      options: [
        {label: "Anoint yourself", outcome: "Soak his favor in a maiden's blood, offer your finger, then finish his invasions.", patterns: ["receiving \"pureblood knight's medal\""], rewards: ["Lord of Blood's Favor", "Bloody Finger", "Pureblood Knight's Medal"]},
        {label: "Decline", outcome: "Reach Mohgwyn through the Consecrated Snowfield waygate instead.", patterns: [], rewards: []}
      ]
    }]
  },
  // Gated areas for quest locations. `match` holds lower-case fragments of quest-step locations; `open` lists
  // alternatives (any one opens the area): boss defeated, all items held, a grace found in a region or by name,
  // or a number of Shardbearer Great Runes. Places matching no entry are always reachable.
  areas: [
    {name: "Leyndell, Ashen Capital", match: ["ashen capital"], regions: ["Leyndell, Ashen Capital"], open: [{boss: "Maliketh, the Black Blade"}], need: "Opens after Maliketh, the Black Blade."},
    {name: "Crumbling Farum Azula", match: ["farum azula"], regions: ["Crumbling Farum Azula"], open: [{boss: "Fire Giant"}, {grace: "Crumbling Farum Azula"}], need: "Opens at the Forge of the Giants after the Fire Giant."},
    {name: "Miquella's Haligtree", match: ["haligtree", "elphael"], regions: ["Miquella's Haligtree", "Elphael, Brace of the Haligtree"], open: [{items: ["Haligtree Secret Medallion (Left)", "Haligtree Secret Medallion (Right)"]}, {grace: "Miquella's Haligtree"}, {grace: "Elphael, Brace of the Haligtree"}], need: "Needs both Haligtree Secret Medallion halves at the Grand Lift of Rold."},
    {name: "Consecrated Snowfield", match: ["consecrated snowfield", "ordina", "yelough", "apostate derelict"], regions: ["Consecrated Snowfield"], open: [{items: ["Haligtree Secret Medallion (Left)", "Haligtree Secret Medallion (Right)"]}, {grace: "Consecrated Snowfield"}], need: "Needs both Haligtree Secret Medallion halves at the Grand Lift of Rold."},
    {name: "Mohgwyn Palace", match: ["mohgwyn"], regions: ["Mohgwyn Palace"], open: [{items: ["Pureblood Knight's Medal"]}, {items: ["Haligtree Secret Medallion (Left)", "Haligtree Secret Medallion (Right)"]}, {grace: "Mohgwyn Palace"}], need: "Needs White Mask Varré's Pureblood Knight's Medal, or the Consecrated Snowfield waygate."},
    {name: "Forge of the Giants", match: ["forge of the giants"], regions: [], open: [{boss: "Fire Giant"}, {graceName: "Forge of the Giants"}], need: "Reached after the Fire Giant at Flame Peak."},
    {name: "Mountaintops of the Giants", match: ["mountaintop", "first church of marika", "stargazers' ruins", "church of repose", "ancient snow valley", "flame peak", "grand lift of rold", "castle sol", "zamor"], regions: ["Mountaintops of the Giants", "Flame Peak"], open: [{items: ["Rold Medallion"]}, {grace: "Mountaintops of the Giants"}], need: "Needs the Rold Medallion, which Melina gives after Morgott."},
    {name: "Leyndell, Royal Capital", match: ["leyndell", "capital rampart", "subterranean shunning", "underground roadside", "cathedral of the forsaken", "royal colosseum", "erdtree sanctuary", "fortified manor"], regions: ["Leyndell, Royal Capital", "Subterranean Shunning-Grounds"], open: [{greatRunes: 2}, {grace: "Leyndell, Royal Capital"}], need: "Needs two Great Runes to pass the gate into Leyndell."},
    {name: "Capital Outskirts", match: ["capital outskirts", "captial outskirts", "outer wall", "minor erdtree church in capital"], regions: ["Capital Outskirts"], open: [{grace: "Altus Plateau"}, {grace: "Capital Outskirts"}], need: "Reached through the Altus Plateau."},
    {name: "Moonlight Altar", match: ["moonlight altar", "cathedral of manus celes"], regions: ["Moonlight Altar"], open: [{boss: "Astel, Naturalborn of the Void"}, {grace: "Moonlight Altar"}], need: "Opens through Ranni's quest after Astel, Naturalborn of the Void."},
    {name: "Divine Tower of Liurnia", match: ["divine tower of liurnia"], regions: [], open: [{items: ["Carian Inverted Statue"]}, {graceName: "Divine Tower of Liurnia"}], need: "Needs the Carian Inverted Statue from Ranni's quest to invert the Carian Study Hall."},
    {name: "Nokron, Eternal City", match: ["nokron", "night's sacred ground", "siofra aqueduct"], regions: ["Nokron, Eternal City"], open: [{boss: "Starscourge Radahn"}, {grace: "Nokron, Eternal City"}], need: "Opens where the star falls after Starscourge Radahn."},
    {name: "Deeproot Depths", match: ["deeproot", "prince of death's throne"], regions: ["Deeproot Depths"], open: [{boss: "Starscourge Radahn"}, {greatRunes: 2}, {grace: "Deeproot Depths"}], need: "Reached from Nokron after Radahn, or through Leyndell's sewers."},
    {name: "Three Sisters", match: ["ranni's rise", "seluvis's rise", "ranni's/seluvis's rise", "renna's rise"], regions: [], open: [{boss: "Royal Knight Loretta"}, {graceName: "Ranni's Rise"}], need: "Reached through Caria Manor after Royal Knight Loretta."},
    {name: "Academy of Raya Lucaria", match: ["raya lucaria grand library", "schoolhouse classroom", "academy"], regions: ["Academy of Raya Lucaria"], open: [{items: ["Academy Glintstone Key"]}, {grace: "Academy of Raya Lucaria"}], need: "Needs the Academy Glintstone Key."},
    {name: "Altus Plateau", match: ["altus", "dominula", "shaded castle", "erdtree-gazing", "hermit village", "fort laiedd", "forest-spanning greatbridge", "mt. gelmir", "primeval sorcerer azur"], regions: ["Altus Plateau", "Mt. Gelmir"], open: [{items: ["Dectus Medallion (Left)", "Dectus Medallion (Right)"]}, {boss: "Magma Wyrm Makar"}, {grace: "Altus Plateau"}, {grace: "Ruin-Strewn Precipice"}], need: "Needs both Dectus Medallion halves, or the Ruin-Strewn Precipice past Magma Wyrm Makar."},
    {name: "Lake of Rot and Ainsel River", match: ["lake of rot", "nokstella", "ainsel"], regions: ["Lake of Rot", "Ainsel River", "Ainsel River Main"], open: []},
    {name: "Volcano Manor", match: ["volcano manor"], regions: ["Volcano Manor"], open: []}
  ],
  // Region names as quest steps write them, for the "not discovered" check outside the gated areas.
  regionAliases: {"limgrave": "Limgrave", "stormhill": "Stormhill", "weeping peninsula": "Weeping Peninsula", "liurnia": "Liurnia of the Lakes", "caelid": "Caelid", "dragonbarrow": "Greyoll's Dragonbarrow", "bellum": "Bellum Highway", "roundtable": "Roundtable Hold", "rth": "Roundtable Hold", "stormveil": "Stormveil Castle", "siofra": "Siofra River", "aeonia": "Swamp of Aeonia"}
};
