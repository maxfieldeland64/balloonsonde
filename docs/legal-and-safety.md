# Legal and safety notes

I am not a lawyer. These are working notes from the planning phase. Verify the current rules before you fly.

## FAA (US free balloons)

Unmanned free balloons are regulated under 14 CFR Part 101, Subpart D. Section 101.1(a)(4) describes what counts as a balloon that **is** subject to the rules. As I understand it, a balloon is covered if it:

- carries a payload package over 4 lb that also exceeds 3 oz per square inch of its smallest surface,
- carries a single package over 6 lb,
- carries multiple packages totaling over 12 lb, or
- uses a suspension line or device that needs more than 50 lb of impact force to separate the payload.

This sonde is about 0.2 lb total, so mass is not close to any limit. The line is the one thing to watch: use a light cord (about 20-30 lb test), not paracord.

Being outside Subpart D does not allow reckless or hazardous operation. In practice:

- Do not launch near airports, flight paths or controlled airspace.
- Check airspace charts and NOTAMs for the launch area. Restricted areas and military operating areas exist in the region.
- Avoid launching toward populated areas or over roads.
- If you are unsure, call the nearest FAA facility before launching.

Current text: search for "14 CFR 101" on ecfr.gov.

## FCC and radio

- The radio is a REYAX RYLR896 LoRa module on 915 MHz (US ISM band). The listing states FCC certification. It is a Part 15 device, so no amateur license is needed.
- Use the supplied antenna. Do not add an amplifier or high-gain antenna, which could take it outside the certification.
- Keep transmit power at or under the module's rated maximum (AT+CRFOP).
- Do not use amateur-band (70 cm) equipment without a license. Recovered used radiosondes (such as Vaisala RS41) transmit around 400-406 MHz; those are fine to receive but not to retransmit or reconfigure without a license.

## Practical safety

- **Helium:** it is an asphyxiant in enclosed spaces. Fill outdoors, secure the cylinder upright, and use a regulator.
- **Fill and launch:** wear eye protection. Do not stand under a taut balloon, and do not fill in gusty wind.
- **Lithium cells:** do not short, crush or charge them. Keep them out of reach of children.
- **Soldering:** use ventilation and eye protection. Wash hands after handling leaded solder.
- **Power lines:** never launch near them, and do not chase the payload onto private land or onto roads in an unsafe way.
- **Recovery:** the payload may land in rough terrain. Plan the recovery as carefully as the launch and tell someone where you are going.
