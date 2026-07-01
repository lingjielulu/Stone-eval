# Short Story CFPG Candidate Review

## Candidates

### to_build_a_fire:ftp_candidate:000001

- Type: `rule` / payoff `literal`
- Distance: 18 paragraphs
- F P0021: The old-timer on Sulphur Creek laid down the law that no man must travel alone in the Klondike after fifty below zero. The man recalls this advice and smiles, thinking the old-timers were womanish.
- T: After his second fire fails and his hands become useless, he realizes he cannot survive alone in the extreme cold, fulfilling the condition warned against.
- P P0039: As the man freezes to death, he mumbles to the old-timer, 'You were right, old hoss; you were right.'
- Rationale: The rule is explicitly stated early and directly fulfilled by the man's death, with a clear trigger in the fire failure.

### to_build_a_fire:ftp_candidate:000002

- Type: `spatial` / payoff `literal`
- Distance: 6 paragraphs
- F P0011-P0012: The man knows about hidden springs under the snow that form traps with water pockets, and he observes the danger of getting wet feet, which would force him to build a fire.
- T: The man encounters an unmarked soft spot on the snow that gives way under his weight, despite his previous caution.
- P P0017: At a place with no visible signs, the man breaks through a hidden spring and wets himself to the knees, which necessitates building a fire to dry his gear.
- Rationale: The spatial trap is described and then encountered, but the interval is relatively short (about five paragraphs), though it is not immediate cause-effect since other events intervene.

### to_build_a_fire:ftp_candidate:000003

- Type: `psychological` / payoff `symbolic`
- Distance: 37 paragraphs
- F P0003: The man, a newcomer, is without imagination and fails to grasp the deadly significance of the extreme cold, viewing it merely as a physical discomfort.
- T: As his body freezes and he can no longer maintain a fire or keep moving, the man's lack of foresight becomes fatal.
- P P0040: The man succumbs to the cold and dies, having never fully comprehended the danger until it was too late.
- Rationale: The psychological flaw is established at the very start and underpins all his decisions, with the payoff being his death. The connection is thematic rather than a single specific event, but it is a clear delayed payoff.

## Verification

### to_build_a_fire:ftp_candidate:000001

- accepted: `True`
- rationale: The foreshadowing in P0021 introduces the warning and the man's overconfidence, which is only fully understood when he faces the fatal consequences of his solitary journey. The payoff in P0039 directly resolves this by having him admit the old-timer was right, making it a genuine narrative payoff rather than a mere thematic echo.
- rejection: 

### to_build_a_fire:ftp_candidate:000002

- accepted: `True`
- rationale: F introduces the specific danger of hidden springs and the necessary response; P fulfills this by having the man fall through one, directly requiring the foreshadowed fire-building. The trigger is a concrete, observable event that explains the timing. There is a non-trivial temporal and narrative gap, and the connection is a causal payoff, not mere thematic echo.
- rejection: 

### to_build_a_fire:ftp_candidate:000003

- accepted: `True`
- rationale: The candidate establishes a clear narrative payback: the early characterization of the man's unimaginative nature directly leads to his inability to heed warnings and ultimately causes his death. The temporal gap, trigger conditions, and non-thematic connection all meet the criteria for a valid foreshadow-trigger-payoff.
- rejection: 
