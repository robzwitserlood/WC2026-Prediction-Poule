# WC2026 Group-Stage Fixtures

Group stage runs 11–27 June 2026. Each group plays 3 rounds; listed home vs away.
Rounds map to matchdays (R1 = first match of each team, etc.). Used by **predict-round** and **run-group-stage**.

**Home/away vs venue:** the first-named team is only a *label*, not the home-advantage signal.
Real home advantage applies only to the three hosts (Mexico, USA, Canada) when playing in
their own country. For every match, the **venue (city/altitude/heat) + kickoff time** is the
condition signal [predict-round] must weight — see its "Venue & conditions" step. Each match
below carries its `@ venue`, with altitude/heat/indoor flags and a per-group conditions note.

**Conditions cheat-sheet:** altitude venues — Mexico City / Estadio Azteca ~2240m (Groups A, K),
Guadalajara / Estadio Akron ~1560m (A, H, K). Indoor/AC (heat neutralised) — SoFi (LA),
AT&T (Arlington), Mercedes-Benz (Atlanta), NRG (Houston), BC Place (retractable, Vancouver).
Hot open-air — Miami (Hard Rock), Monterrey (Estadio BBVA), Kansas City (Arrowhead), East-Coast
outdoor in late June. Cool/mild — Vancouver, Seattle, Toronto, Foxborough. Host home edge:
Mexico (A, K venues at home), USA (D), Canada (B). Kickoff times not captured; if heat-vs-time
matters for a specific pick, refresh the time then.

Sources: ESPN/FIFA fixtures pages; per-group Wikipedia "2026 FIFA World Cup Group X" and Sky Sports group guides; Yahoo daily schedule (venues fetched 2026-06-09).

## Group A
*(venues verified 2026-06-09; Mexico City ~2240m, Guadalajara/Zapopan/Guadalupe ~1560m — altitude is a real factor here; Atlanta is a roofed/AC stadium, summer heat otherwise)*
- **R1** — Jun 11: Mexico vs South Africa @ Mexico City (alt ~2240m) · Jun 11: South Korea vs Czechia @ Zapopan/Guadalajara (alt ~1560m)
- **R2** — Jun 18: Czechia vs South Africa @ Atlanta (indoor/AC) · Jun 18: Mexico vs South Korea @ Zapopan/Guadalajara (alt ~1560m)
- **R3** — Jun 24: Czechia vs Mexico @ Mexico City (alt ~2240m) · Jun 24: South Africa vs South Korea @ Guadalupe/Guadalajara (alt ~1560m)

## Group B
*(Canada home matches at Toronto/Vancouver — real host advantage. All venues cool/temperate or indoor; no altitude.)*
- **R1** — Jun 12: Canada vs Bosnia and Herzegovina @ Toronto (BMO Field; Canada home) · Jun 13: Qatar vs Switzerland @ Santa Clara (Levi's Stadium)
- **R2** — Jun 18: Switzerland vs Bosnia and Herzegovina @ Los Angeles (SoFi Stadium, indoor/AC) · Jun 18: Canada vs Qatar @ Vancouver (BC Place, retractable roof; Canada home)
- **R3** — Jun 24: Switzerland vs Canada @ Vancouver (BC Place; Canada home) · Jun 24: Bosnia and Herzegovina vs Qatar @ Seattle (Lumen Field)

## Group C
*(US East Coast + Miami — summer heat/humidity, no altitude. Miami especially hot/humid in late June; Scotland's cool-climate squad most exposed.)*
- **R1** — Jun 13: Brazil vs Morocco @ East Rutherford NJ (MetLife Stadium) · Jun 13: Haiti vs Scotland @ Foxborough MA (Gillette Stadium)
- **R2** — Jun 19: Scotland vs Morocco @ Foxborough MA (Gillette Stadium) · Jun 19: Brazil vs Haiti @ Philadelphia (Lincoln Financial Field)
- **R3** — Jun 24: Scotland vs Brazil @ Miami (Hard Rock Stadium; heat/humidity) · Jun 24: Morocco vs Haiti @ Atlanta (Mercedes-Benz Stadium, indoor/AC)

## Group D
*(West Coast US + Vancouver — mild/temperate, mostly indoor/AC. USA home edge at SoFi/Seattle. No altitude; least heat-stressed group.)*
- **R1** — Jun 12: United States vs Paraguay @ Los Angeles (SoFi Stadium, indoor/AC; USA home) · Jun 13: Australia vs Türkiye @ Vancouver (BC Place)
- **R2** — Jun 19: United States vs Australia @ Seattle (Lumen Field; USA home) · Jun 19: Türkiye vs Paraguay @ Santa Clara (Levi's Stadium)
- **R3** — Jun 25: Türkiye vs United States @ Los Angeles (SoFi Stadium, indoor/AC; USA home) · Jun 25: Paraguay vs Australia @ Santa Clara (Levi's Stadium)

## Group E
*(Houston heat (NRG is indoor/AC), Philadelphia/KC/Toronto. No altitude. Germany's deep cool-climate squad vs heat at Houston a watch.)*
- **R1** — Jun 14: Germany vs Curaçao @ Houston (NRG Stadium, indoor/AC) · Jun 14: Ivory Coast vs Ecuador @ Philadelphia (Lincoln Financial Field)
- **R2** — Jun 20: Germany vs Ivory Coast @ Toronto (BMO Field) · Jun 20: Ecuador vs Curaçao @ Kansas City (Arrowhead Stadium; heat)
- **R3** — Jun 25: Ecuador vs Germany @ East Rutherford NJ (MetLife Stadium) · Jun 25: Curaçao vs Ivory Coast @ Philadelphia (Lincoln Financial Field)

## Group F
*(Monterrey (Estadio BBVA, open-air, extreme June heat ~540m), Arlington/Houston (indoor/AC), KC. Sweden's cool-climate squad most exposed in the two Monterrey games.)*
- **R1** — Jun 14: Netherlands vs Japan @ Arlington TX (AT&T Stadium, indoor/AC) · Jun 14: Sweden vs Tunisia @ Monterrey MX (Estadio BBVA; open-air heat)
- **R2** — Jun 20: Netherlands vs Sweden @ Houston (NRG Stadium, indoor/AC) · Jun 20: Tunisia vs Japan @ Monterrey MX (Estadio BBVA; open-air heat)
- **R3** — Jun 25: Japan vs Sweden @ Arlington TX (AT&T Stadium, indoor/AC) · Jun 25: Tunisia vs Netherlands @ Kansas City (Arrowhead Stadium; heat)

## Group G
*(West Coast/Vancouver — mild, temperate, mostly indoor. No altitude/heat stress.)*
- **R1** — Jun 15: Belgium vs Egypt @ Seattle (Lumen Field) · Jun 15: Iran vs New Zealand @ Los Angeles (SoFi Stadium, indoor/AC)
- **R2** — Jun 21: Belgium vs Iran @ Los Angeles (SoFi Stadium, indoor/AC) · Jun 21: New Zealand vs Egypt @ Vancouver (BC Place)
- **R3** — Jun 26: Egypt vs Iran @ Seattle (Lumen Field) · Jun 26: New Zealand vs Belgium @ Vancouver (BC Place)

## Group H
*(Atlanta/Miami/Houston heat (first two indoor/AC) then R3 splits — Uruguay-Spain at Guadalajara altitude ~1560m. Miami humidity a factor R1.)*
- **R1** — Jun 15: Spain vs Cape Verde @ Atlanta (Mercedes-Benz Stadium, indoor/AC) · Jun 15: Saudi Arabia vs Uruguay @ Miami (Hard Rock Stadium; heat/humidity)
- **R2** — Jun 21: Spain vs Saudi Arabia @ Atlanta (Mercedes-Benz Stadium, indoor/AC) · Jun 21: Uruguay vs Cape Verde @ Miami (Hard Rock Stadium; heat/humidity)
- **R3** — Jun 26: Cape Verde vs Saudi Arabia @ Houston (NRG Stadium, indoor/AC) · Jun 26: Uruguay vs Spain @ Guadalajara MX (Estadio Akron; alt ~1560m)

## Group I
*(US East Coast + Toronto — summer heat/humidity, no altitude. Norway's cool-climate squad most exposed; Iraq/Senegal acclimatised to heat.)*
- **R1** — Jun 16: France vs Senegal @ East Rutherford NJ (MetLife Stadium) · Jun 16: Iraq vs Norway @ Foxborough MA (Gillette Stadium)
- **R2** — Jun 22: France vs Iraq @ Philadelphia (Lincoln Financial Field) · Jun 22: Norway vs Senegal @ East Rutherford NJ (MetLife Stadium)
- **R3** — Jun 26: Norway vs France @ Foxborough MA (Gillette Stadium) · Jun 26: Senegal vs Iraq @ Toronto (BMO Field)

## Group J
*(Kansas City heat (open-air Arrowhead), Arlington (AT&T indoor/AC), Santa Clara (mild). No altitude. Austria's cool-climate squad most exposed at KC; Algeria/Jordan heat-adapted.)*
- **R1** — Jun 16: Argentina vs Algeria @ Kansas City (Arrowhead Stadium; heat) · Jun 16: Austria vs Jordan @ Santa Clara (Levi's Stadium)
- **R2** — Jun 22: Argentina vs Austria @ Arlington TX (AT&T Stadium, indoor/AC) · Jun 22: Jordan vs Algeria @ Santa Clara (Levi's Stadium)
- **R3** — Jun 27: Algeria vs Austria @ Kansas City (Arrowhead Stadium; heat) · Jun 27: Jordan vs Argentina @ Arlington TX (AT&T Stadium, indoor/AC)

## Group K
*(Strongest altitude group: Colombia play 2 of 3 at altitude (Mexico City ~2240m, Guadalajara ~1560m) — they're Andean-acclimatised, a real edge the crowd underrates. Portugal stay in hot Houston/Miami. Watch Colombia value.)*
- **R1** — Jun 17: Portugal vs DR Congo @ Houston (NRG Stadium, indoor/AC) · Jun 17: Uzbekistan vs Colombia @ Mexico City (Estadio Azteca; alt ~2240m)
- **R2** — Jun 23: Portugal vs Uzbekistan @ Houston (NRG Stadium, indoor/AC) · Jun 23: Colombia vs DR Congo @ Guadalajara MX (Estadio Akron; alt ~1560m)
- **R3** — Jun 27: Colombia vs Portugal @ Miami (Hard Rock Stadium; heat/humidity) · Jun 27: DR Congo vs Uzbekistan @ Atlanta (Mercedes-Benz Stadium, indoor/AC)

## Group L
*(Arlington (AT&T indoor/AC), Toronto, Foxborough, Philadelphia, NY/NJ. No altitude; East-Coast summer heat outdoors. Ghana/Panama heat-adapted; England/Croatia cooler-climate.)*
- **R1** — Jun 17: England vs Croatia @ Arlington TX (AT&T Stadium, indoor/AC) · Jun 17: Ghana vs Panama @ Toronto (BMO Field)
- **R2** — Jun 23: England vs Ghana @ Foxborough MA (Gillette Stadium) · Jun 23: Panama vs Croatia @ Foxborough MA (Gillette Stadium)
- **R3** — Jun 27: Panama vs England @ East Rutherford NJ (MetLife Stadium) · Jun 27: Croatia vs Ghana @ Philadelphia (Lincoln Financial Field)
