# Short Story CFPG Candidate Review

## Candidates

### necklace:ftp_candidate:000001

- Type: `object` / payoff `delayed_revelation`
- Distance: 76 paragraphs
- F P0046-P0048: Mathilde finds a superb diamond necklace in a black satin box at Madame Forestier's, her heart throbs with immoderate desire, and she puts it on in ecstasy.
- T: Mathilde loses the necklace after the ball and is forced to replace it with a genuine diamond necklace at great cost.
- P P0122: Madame Forestier reveals that the original necklace was paste and worth only five hundred francs.
- Rationale: This is the central twist of the story, fitting the object-foreshadow pattern perfectly.

### necklace:ftp_candidate:000002

- Type: `psychological` / payoff `ironic`
- Distance: 98 paragraphs
- F P0001-P0005: Mathilde is deeply unhappy with her modest circumstances, constantly dreaming of luxury and elegance, and feeling she was born for a higher station.
- T: The loss of the necklace forces the Loisels into a decade of harsh toil to repay the replacement debt.
- P P0099: After ten years of poverty, Mathilde has become a strong, rough woman with frowsy hair and red hands, who only occasionally remembers the ball where she was beautiful.
- Rationale: Although this is a character trait rather than a concrete object, it functions as a motivational foreshadow that is paid off with the decay of her beauty and status.

### necklace:ftp_candidate:000003

- Type: `retrospective` / payoff `delayed_revelation`
- Distance: 81 paragraphs
- F P0041-P0050: Madame Forestier generously and casually lends Mathilde any jewel she wants, including the diamond necklace, without hesitation.
- T: Madame Forestier reacts indifferently when the necklace is returned, not even inspecting it.
- P P0122: Madame Forestier reveals the necklace was paste, suggesting she was never worried about the loan because of its low value.
- Rationale: This is a subtle behavioral clue that only becomes meaningful after the twist reveal; less central than the necklace object itself.

## Verification

### necklace:ftp_candidate:000001

- accepted: `True`
- rationale: The setup introduces the necklace's assumed high value, unresolved. The payoff reveals it was fake, directly resolving the setup. The trigger (losing and replacing it) is observable and explains why the truth emerges later. The connection is a narrative payoff, not thematic echo.
- rejection: 

### necklace:ftp_candidate:000002

- accepted: `True`
- rationale: The foreshadowing of her dissatisfaction with her station sets up the ironic reversal where her pursuit of a single night of splendor leads to a life of even greater hardship, transforming her into the very type of woman she once pitied. The payoff shows the physical and social decay resulting from the trigger (loss of the necklace and subsequent debt).
- rejection: 

### necklace:ftp_candidate:000003

- accepted: `False`
- rationale: The provided setup window (P0039-P0043) does not include the crucial casual lending of the diamond necklace, which is the supposed foreshadowing. Thus, the connection between the setup and payoff cannot be verified from the given windows. Additional plot details (the trigger of returning without inspection) are also outside the provided windows.
- rejection: Setup window lacks the specific foreshadowing event (casual lending of the necklace), making the setup incomplete. Without this, the payoff cannot be seen as a resolution of an earlier narrative element.
