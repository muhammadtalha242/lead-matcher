import json

# Multiline string containing all NACE codes and descriptions
nace_data_eng = """
A - Agriculture, forestry and fishing
A1 - Crop and animal production, hunting and related service activities
A1.1 - Growing of non-perennial crops
A1.1.1 - Growing of cereals (except rice), leguminous crops and oil seeds
A1.1.2 - Growing of rice
A1.1.3 - Growing of vegetables and melons, roots and tubers
A1.1.4 - Growing of sugar cane
A1.1.5 - Growing of tobacco
A1.1.6 - Growing of fibre crops
A1.1.9 - Growing of other non-perennial crops
A1.2 - Growing of perennial crops
A1.2.1 - Growing of grapes
A1.2.2 - Growing of tropical and subtropical fruits
A1.2.3 - Growing of citrus fruits
A1.2.4 - Growing of pome fruits and stone fruits
A1.2.5 - Growing of other tree and bush fruits and nuts
A1.2.6 - Growing of oleaginous fruits
A1.2.7 - Growing of beverage crops
A1.2.8 - Growing of spices, aromatic, drug and pharmaceutical crops
A1.2.9 - Growing of other perennial crops
A1.3 - Plant propagation
A1.3.0 - Plant propagation
A1.4 - Animal production
A1.4.1 - Raising of dairy cattle
A1.4.2 - Raising of other cattle and buffaloes
A1.4.3 - Raising of horses and other equines
A1.4.4 - Raising of camels and camelids
A1.4.5 - Raising of sheep and goats
A1.4.6 - Raising of swine/pigs
A1.4.7 - Raising of poultry
A1.4.9 - Raising of other animals
A1.5 - Mixed farming
A1.5.0 - Mixed farming
A1.6 - Support activities to agriculture and post-harvest crop activities
A1.6.1 - Support activities for crop production
A1.6.2 - Support activities for animal production
A1.6.3 - Post-harvest crop activities
A1.6.4 - Seed processing for propagation
A1.7 - Hunting, trapping and related service activities
A1.7.0 - Hunting, trapping and related service activities
A2 - Forestry and logging
A2.1 - Silviculture and other forestry activities
A2.1.0 - Silviculture and other forestry activities
A2.2 - Logging
A2.2.0 - Logging
A2.3 - Gathering of wild growing non-wood products
A2.3.0 - Gathering of wild growing non-wood products
A2.4 - Support services to forestry
A2.4.0 - Support services to forestry
A3 - Fishing and aquaculture
A3.1 - Fishing
A3.1.1 - Marine fishing
A3.1.2 - Freshwater fishing
A3.2 - Aquaculture
A3.2.1 - Marine aquaculture
A3.2.2 - Freshwater aquaculture
B - Mining and quarrying
B5 - Mining of coal and lignite
B5.1 - Mining of hard coal
B5.1.0 - Mining of hard coal
B5.2 - Mining of lignite
B5.2.0 - Mining of lignite
B6 - Extraction of crude petroleum and natural gas
B6.1 - Extraction of crude petroleum
B6.1.0 - Extraction of crude petroleum
B6.2 - Extraction of natural gas
B6.2.0 - Extraction of natural gas
B7 - Mining of metal ores
B7.1 - Mining of iron ores
B7.1.0 - Mining of iron ores
B7.2 - Mining of non-ferrous metal ores
B7.2.1 - Mining of uranium and thorium ores
B7.2.9 - Mining of other non-ferrous metal ores
B8 - Other mining and quarrying
B8.1 - Quarrying of stone, sand and clay
B8.1.1 - Quarrying of ornamental and building stone, limestone, gypsum, chalk and slate
B8.1.2 - Operation of gravel and sand pits; mining of clays and kaolin
B8.9 - Mining and quarrying n.e.c.
B8.9.1 - Mining of chemical and fertiliser minerals
B8.9.2 - Extraction of peat
B8.9.3 - Extraction of salt
B8.9.9 - Other mining and quarrying n.e.c.
B9 - Mining support service activities
B9.1 - Support activities for petroleum and natural gas extraction
B9.1.0 - Support activities for petroleum and natural gas extraction
B9.9 - Support activities for other mining and quarrying
B9.9.0 - Support activities for other mining and quarrying
C - Manufacturing
C10 - Manufacture of food products
C10.1 - Processing and preserving of meat and production of meat products
C10.1.1 - Processing and preserving of meat
C10.1.2 - Processing and preserving of poultry meat
C10.1.3 - Production of meat and poultry meat products
C10.2 - Processing and preserving of fish, crustaceans and molluscs
C10.2.0 - Processing and preserving of fish, crustaceans and molluscs
C10.3 - Processing and preserving of fruit and vegetables
C10.3.1 - Processing and preserving of potatoes
C10.3.2 - Manufacture of fruit and vegetable juice
C10.3.9 - Other processing and preserving of fruit and vegetables
C10.4 - Manufacture of vegetable and animal oils and fats
C10.4.1 - Manufacture of oils and fats
C10.4.2 - Manufacture of margarine and similar edible fats
C10.5 - Manufacture of dairy products
C10.5.1 - Operation of dairies and cheese making
C10.5.2 - Manufacture of ice cream
C10.6 - Manufacture of grain mill products, starches and starch products
C10.6.1 - Manufacture of grain mill products
C10.6.2 - Manufacture of starches and starch products
C10.7 - Manufacture of bakery and farinaceous products
C10.7.1 - Manufacture of bread; manufacture of fresh pastry goods and cakes
C10.7.2 - Manufacture of rusks and biscuits; manufacture of preserved pastry goods and cakes
C10.7.3 - Manufacture of macaroni, noodles, couscous and similar farinaceous products
C10.8 - Manufacture of other food products
C10.8.1 - Manufacture of sugar
C10.8.2 - Manufacture of cocoa, chocolate and sugar confectionery
C10.8.3 - Processing of tea and coffee
C10.8.4 - Manufacture of condiments and seasonings
C10.8.5 - Manufacture of prepared meals and dishes
C10.8.6 - Manufacture of homogenised food preparations and dietetic food
C10.8.9 - Manufacture of other food products n.e.c.
C10.9 - Manufacture of prepared animal feeds
C10.9.1 - Manufacture of prepared feeds for farm animals
C10.9.2 - Manufacture of prepared pet foods
C11 - Manufacture of beverages
C11.0 - Manufacture of beverages
C11.0.1 - Distilling, rectifying and blending of spirits
C11.0.2 - Manufacture of wine from grape
C11.0.3 - Manufacture of cider and other fruit wines
C11.0.4 - Manufacture of other non-distilled fermented beverages
C11.0.5 - Manufacture of beer
C11.0.6 - Manufacture of malt
C11.0.7 - Manufacture of soft drinks; production of mineral waters and other bottled waters
C12 - Manufacture of tobacco products
C12.0 - Manufacture of tobacco products
C12.0.0 - Manufacture of tobacco products
C13 - Manufacture of textiles
C13.1 - Preparation and spinning of textile fibres
C13.1.0 - Preparation and spinning of textile fibres
C13.2 - Weaving of textiles
C13.2.0 - Weaving of textiles
C13.3 - Finishing of textiles
C13.3.0 - Finishing of textiles
C13.9 - Manufacture of other textiles
C13.9.1 - Manufacture of knitted and crocheted fabrics
C13.9.2 - Manufacture of made-up textile articles, except apparel
C13.9.3 - Manufacture of carpets and rugs
C13.9.4 - Manufacture of cordage, rope, twine and netting
C13.9.5 - Manufacture of non-wovens and articles made from non-wovens, except apparel
C13.9.6 - Manufacture of other technical and industrial textiles
C13.9.9 - Manufacture of other textiles n.e.c.
C14 - Manufacture of wearing apparel
C14.1 - Manufacture of wearing apparel, except fur apparel
C14.1.1 - Manufacture of leather clothes
C14.1.2 - Manufacture of workwear
C14.1.3 - Manufacture of other outerwear
C14.1.4 - Manufacture of underwear
C14.1.9 - Manufacture of other wearing apparel and accessories
C14.2 - Manufacture of articles of fur
C14.2.0 - Manufacture of articles of fur
C14.3 - Manufacture of knitted and crocheted apparel
C14.3.1 - Manufacture of knitted and crocheted hosiery
C14.3.9 - Manufacture of other knitted and crocheted apparel
C15 - Manufacture of leather and related products
C15.1 - Tanning and dressing of leather; manufacture of luggage, handbags, saddlery and harness; dressing and dyeing of fur
C15.1.1 - Tanning and dressing of leather; dressing and dyeing of fur
C15.1.2 - Manufacture of luggage, handbags and the like, saddlery and harness
C15.2 - Manufacture of footwear
C15.2.0 - Manufacture of footwear
C16 - Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials
C16.1 - Sawmilling and planing of wood
C16.1.0 - Sawmilling and planing of wood
C16.2 - Manufacture of products of wood, cork, straw and plaiting materials
C16.2.1 - Manufacture of veneer sheets and wood-based panels
C16.2.2 - Manufacture of assembled parquet floors
C16.2.3 - Manufacture of other builders' carpentry and joinery
C16.2.4 - Manufacture of wooden containers
C16.2.9 - Manufacture of other products of wood; manufacture of articles of cork, straw and plaiting materials
C17 - Manufacture of paper and paper products
C17.1 - Manufacture of pulp, paper and paperboard
C17.1.1 - Manufacture of pulp
C17.1.2 - Manufacture of paper and paperboard
C17.2 - Manufacture of articles of paper and paperboard
C17.2.1 - Manufacture of corrugated paper and paperboard and of containers of paper and paperboard
C17.2.2 - Manufacture of household and sanitary goods and of toilet requisites
C17.2.3 - Manufacture of paper stationery
C17.2.4 - Manufacture of wallpaper
C17.2.9 - Manufacture of other articles of paper and paperboard
C18 - Printing and reproduction of recorded media
C18.1 - Printing and service activities related to printing
C18.1.1 - Printing of newspapers
C18.1.2 - Other printing
C18.1.3 - Pre-press and pre-media services
C18.1.4 - Binding and related services
C18.2 - Reproduction of recorded media
C18.2.0 - Reproduction of recorded media
C19 - Manufacture of coke and refined petroleum products
C19.1 - Manufacture of coke oven products
C19.1.0 - Manufacture of coke oven products
C19.2 - Manufacture of refined petroleum products
C19.2.0 - Manufacture of refined petroleum products
C20 - Manufacture of chemicals and chemical products
C20.1 - Manufacture of basic chemicals, fertilisers and nitrogen compounds, plastics and synthetic rubber in primary forms
C20.1.1 - Manufacture of industrial gases
C20.1.2 - Manufacture of dyes and pigments
C20.1.3 - Manufacture of other inorganic basic chemicals
C20.1.4 - Manufacture of other organic basic chemicals
C20.1.5 - Manufacture of fertilisers and nitrogen compounds
C20.1.6 - Manufacture of plastics in primary forms
C20.1.7 - Manufacture of synthetic rubber in primary forms
C20.2 - Manufacture of pesticides and other agrochemical products
C20.2.0 - Manufacture of pesticides and other agrochemical products
C20.3 - Manufacture of paints, varnishes and similar coatings, printing ink and mastics
C20.3.0 - Manufacture of paints, varnishes and similar coatings, printing ink and mastics
C20.4 - Manufacture of soap and detergents, cleaning and polishing preparations, perfumes and toilet preparations
C20.4.1 - Manufacture of soap and detergents, cleaning and polishing preparations
C20.4.2 - Manufacture of perfumes and toilet preparations
C20.5 - Manufacture of other chemical products
C20.5.1 - Manufacture of explosives
C20.5.2 - Manufacture of glues
C20.5.3 - Manufacture of essential oils
C20.5.9 - Manufacture of other chemical products n.e.c.
C20.6 - Manufacture of man-made fibres
C20.6.0 - Manufacture of man-made fibres
C21 - Manufacture of basic pharmaceutical products and pharmaceutical preparations
C21.1 - Manufacture of basic pharmaceutical products
C21.1.0 - Manufacture of basic pharmaceutical products
C21.2 - Manufacture of pharmaceutical preparations
C21.2.0 - Manufacture of pharmaceutical preparations
C22 - Manufacture of rubber and plastic products
C22.1 - Manufacture of rubber products
C22.1.1 - Manufacture of rubber tyres and tubes; retreading and rebuilding of rubber tyres
C22.1.9 - Manufacture of other rubber products
C22.2 - Manufacture of plastics products
C22.2.1 - Manufacture of plastic plates, sheets, tubes and profiles
C22.2.2 - Manufacture of plastic packing goods
C22.2.3 - Manufacture of builders’ ware of plastic
C22.2.9 - Manufacture of other plastic products
C23 - Manufacture of other non-metallic mineral products
C23.1 - Manufacture of glass and glass products
C23.1.1 - Manufacture of flat glass
C23.1.2 - Shaping and processing of flat glass
C23.1.3 - Manufacture of hollow glass
C23.1.4 - Manufacture of glass fibres
C23.1.9 - Manufacture and processing of other glass, including technical glassware
C23.2 - Manufacture of refractory products
C23.2.0 - Manufacture of refractory products
C23.3 - Manufacture of clay building materials
C23.3.1 - Manufacture of ceramic tiles and flags
C23.3.2 - Manufacture of bricks, tiles and construction products, in baked clay
C23.4 - Manufacture of other porcelain and ceramic products
C23.4.1 - Manufacture of ceramic household and ornamental articles
C23.4.2 - Manufacture of ceramic sanitary fixtures
C23.4.3 - Manufacture of ceramic insulators and insulating fittings
C23.4.4 - Manufacture of other technical ceramic products
C23.4.9 - Manufacture of other ceramic products
C23.5 - Manufacture of cement, lime and plaster
C23.5.1 - Manufacture of cement
C23.5.2 - Manufacture of lime and plaster
C23.6 - Manufacture of articles of concrete, cement and plaster
C23.6.1 - Manufacture of concrete products for construction purposes
C23.6.2 - Manufacture of plaster products for construction purposes
C23.6.3 - Manufacture of ready-mixed concrete
C23.6.4 - Manufacture of mortars
C23.6.5 - Manufacture of fibre cement
C23.6.9 - Manufacture of other articles of concrete, plaster and cement
C23.7 - Cutting, shaping and finishing of stone
C23.7.0 - Cutting, shaping and finishing of stone
C23.9 - Manufacture of abrasive products and non-metallic mineral products n.e.c.
C23.9.1 - Production of abrasive products
C23.9.9 - Manufacture of other non-metallic mineral products n.e.c.
C24 - Manufacture of basic metals
C24.1 - Manufacture of basic iron and steel and of ferro-alloys
C24.1.0 - Manufacture of basic iron and steel and of ferro-alloys
C24.2 - Manufacture of tubes, pipes, hollow profiles and related fittings, of steel
C24.2.0 - Manufacture of tubes, pipes, hollow profiles and related fittings, of steel
C24.3 - Manufacture of other products of first processing of steel
C24.3.1 - Cold drawing of bars
C24.3.2 - Cold rolling of narrow strip
C24.3.3 - Cold forming or folding
C24.3.4 - Cold drawing of wire
C24.4 - Manufacture of basic precious and other non-ferrous metals
C24.4.1 - Precious metals production
C24.4.2 - Aluminium production
C24.4.3 - Lead, zinc and tin production
C24.4.4 - Copper production
C24.4.5 - Other non-ferrous metal production
C24.4.6 - Processing of nuclear fuel
C24.5 - Casting of metals
C24.5.1 - Casting of iron
C24.5.2 - Casting of steel
C24.5.3 - Casting of light metals
C24.5.4 - Casting of other non-ferrous metals
C25 - Manufacture of fabricated metal products, except machinery and equipment
C25.1 - Manufacture of structural metal products
C25.1.1 - Manufacture of metal structures and parts of structures
C25.1.2 - Manufacture of doors and windows of metal
C25.2 - Manufacture of tanks, reservoirs and containers of metal
C25.2.1 - Manufacture of central heating radiators and boilers
C25.2.9 - Manufacture of other tanks, reservoirs and containers of metal
C25.3 - Manufacture of steam generators, except central heating hot water boilers
C25.3.0 - Manufacture of steam generators, except central heating hot water boilers
C25.4 - Manufacture of weapons and ammunition
C25.4.0 - Manufacture of weapons and ammunition
C25.5 - Forging, pressing, stamping and roll-forming of metal; powder metallurgy
C25.5.0 - Forging, pressing, stamping and roll-forming of metal; powder metallurgy
C25.6 - Treatment and coating of metals; machining
C25.6.1 - Treatment and coating of metals
C25.6.2 - Machining
C25.7 - Manufacture of cutlery, tools and general hardware
C25.7.1 - Manufacture of cutlery
C25.7.2 - Manufacture of locks and hinges
C25.7.3 - Manufacture of tools
C25.9 - Manufacture of other fabricated metal products
C25.9.1 - Manufacture of steel drums and similar containers
C25.9.2 - Manufacture of light metal packaging
C25.9.3 - Manufacture of wire products, chain and springs
C25.9.4 - Manufacture of fasteners and screw machine products
C25.9.9 - Manufacture of other fabricated metal products n.e.c.
C26 - Manufacture of computer, electronic and optical products
C26.1 - Manufacture of electronic components and boards
C26.1.1 - Manufacture of electronic components
C26.1.2 - Manufacture of loaded electronic boards
C26.2 - Manufacture of computers and peripheral equipment
C26.2.0 - Manufacture of computers and peripheral equipment
C26.3 - Manufacture of communication equipment
C26.3.0 - Manufacture of communication equipment
C26.4 - Manufacture of consumer electronics
C26.4.0 - Manufacture of consumer electronics
C26.5 - Manufacture of instruments and appliances for measuring, testing and navigation; watches and clocks
C26.5.1 - Manufacture of instruments and appliances for measuring, testing and navigation
C26.5.2 - Manufacture of watches and clocks
C26.6 - Manufacture of irradiation, electromedical and electrotherapeutic equipment
C26.6.0 - Manufacture of irradiation, electromedical and electrotherapeutic equipment
C26.7 - Manufacture of optical instruments and photographic equipment
C26.7.0 - Manufacture of optical instruments and photographic equipment
C26.8 - Manufacture of magnetic and optical media
C26.8.0 - Manufacture of magnetic and optical media
C27 - Manufacture of electrical equipment
C27.1 - Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus
C27.1.1 - Manufacture of electric motors, generators and transformers
C27.1.2 - Manufacture of electricity distribution and control apparatus
C27.2 - Manufacture of batteries and accumulators
C27.2.0 - Manufacture of batteries and accumulators
C27.3 - Manufacture of wiring and wiring devices
C27.3.1 - Manufacture of fibre optic cables
C27.3.2 - Manufacture of other electronic and electric wires and cables
C27.3.3 - Manufacture of wiring devices
C27.4 - Manufacture of electric lighting equipment
C27.4.0 - Manufacture of electric lighting equipment
C27.5 - Manufacture of domestic appliances
C27.5.1 - Manufacture of electric domestic appliances
C27.5.2 - Manufacture of non-electric domestic appliances
C27.9 - Manufacture of other electrical equipment
C27.9.0 - Manufacture of other electrical equipment
C28 - Manufacture of machinery and equipment n.e.c.
C28.1 - Manufacture of general-purpose machinery
C28.1.1 - Manufacture of engines and turbines, except aircraft, vehicle and cycle engines
C28.1.2 - Manufacture of fluid power equipment
C28.1.3 - Manufacture of other pumps and compressors
C28.1.4 - Manufacture of other taps and valves
C28.1.5 - Manufacture of bearings, gears, gearing and driving elements
C28.2 - Manufacture of other general-purpose machinery
C28.2.1 - Manufacture of ovens, furnaces and furnace burners
C28.2.2 - Manufacture of lifting and handling equipment
C28.2.3 - Manufacture of office machinery and equipment (except computers and peripheral equipment)
C28.2.4 - Manufacture of power-driven hand tools
C28.2.5 - Manufacture of non-domestic cooling and ventilation equipment
C28.2.9 - Manufacture of other general-purpose machinery n.e.c.
C28.3 - Manufacture of agricultural and forestry machinery
C28.3.0 - Manufacture of agricultural and forestry machinery
C28.4 - Manufacture of metal forming machinery and machine tools
C28.4.1 - Manufacture of metal forming machinery
C28.4.9 - Manufacture of other machine tools
C28.9 - Manufacture of other special-purpose machinery
C28.9.1 - Manufacture of machinery for metallurgy
C28.9.2 - Manufacture of machinery for mining, quarrying and construction
C28.9.3 - Manufacture of machinery for food, beverage and tobacco processing
C28.9.4 - Manufacture of machinery for textile, apparel and leather production
C28.9.5 - Manufacture of machinery for paper and paperboard production
C28.9.6 - Manufacture of plastics and rubber machinery
C28.9.9 - Manufacture of other special-purpose machinery n.e.c.
C29 - Manufacture of motor vehicles, trailers and semi-trailers
C29.1 - Manufacture of motor vehicles
C29.1.0 - Manufacture of motor vehicles
C29.2 - Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers
C29.2.0 - Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers
C29.3 - Manufacture of parts and accessories for motor vehicles
C29.3.1 - Manufacture of electrical and electronic equipment for motor vehicles
C29.3.2 - Manufacture of other parts and accessories for motor vehicles
C30 - Manufacture of other transport equipment
C30.1 - Building of ships and boats
C30.1.1 - Building of ships and floating structures
C30.1.2 - Building of pleasure and sporting boats
C30.2 - Manufacture of railway locomotives and rolling stock
C30.2.0 - Manufacture of railway locomotives and rolling stock
C30.3 - Manufacture of air and spacecraft and related machinery
C30.3.0 - Manufacture of air and spacecraft and related machinery
C30.4 - Manufacture of military fighting vehicles
C30.4.0 - Manufacture of military fighting vehicles
C30.9 - Manufacture of transport equipment n.e.c.
C30.9.1 - Manufacture of motorcycles
C30.9.2 - Manufacture of bicycles and invalid carriages
C30.9.9 - Manufacture of other transport equipment n.e.c.
C31 - Manufacture of furniture
C31.0 - Manufacture of furniture
C31.0.1 - Manufacture of office and shop furniture
C31.0.2 - Manufacture of kitchen furniture
C31.0.3 - Manufacture of mattresses
C31.0.9 - Manufacture of other furniture
C32 - Other manufacturing
C32.1 - Manufacture of jewellery, bijouterie and related articles
C32.1.1 - Striking of coins
C32.1.2 - Manufacture of jewellery and related articles
C32.1.3 - Manufacture of imitation jewellery and related articles
C32.2 - Manufacture of musical instruments
C32.2.0 - Manufacture of musical instruments
C32.3 - Manufacture of sports goods
C32.3.0 - Manufacture of sports goods
C32.4 - Manufacture of games and toys
C32.4.0 - Manufacture of games and toys
C32.5 - Manufacture of medical and dental instruments and supplies
C32.5.0 - Manufacture of medical and dental instruments and supplies
C32.9 - Manufacturing n.e.c.
C32.9.1 - Manufacture of brooms and brushes
C32.9.9 - Other manufacturing n.e.c.
C33 - Repair and installation of machinery and equipment
C33.1 - Repair of fabricated metal products, machinery and equipment
C33.1.1 - Repair of fabricated metal products
C33.1.2 - Repair of machinery
C33.1.3 - Repair of electronic and optical equipment
C33.1.4 - Repair of electrical equipment
C33.1.5 - Repair and maintenance of ships and boats
C33.1.6 - Repair and maintenance of aircraft and spacecraft
C33.1.7 - Repair and maintenance of other transport equipment
C33.1.9 - Repair of other equipment
C33.2 - Installation of industrial machinery and equipment
C33.2.0 - Installation of industrial machinery and equipment
D - Electricity, gas, steam and air conditioning supply
D35 - Electricity, gas, steam and air conditioning supply
D35.1 - Electric power generation, transmission and distribution
D35.1.1 - Production of electricity
D35.1.2 - Transmission of electricity
D35.1.3 - Distribution of electricity
D35.1.4 - Trade of electricity
D35.2 - Manufacture of gas; distribution of gaseous fuels through mains
D35.2.1 - Manufacture of gas
D35.2.2 - Distribution of gaseous fuels through mains
D35.2.3 - Trade of gas through mains
D35.3 - Steam and air conditioning supply
D35.3.0 - Steam and air conditioning supply
E - Water supply; sewerage; waste managment and remediation activities
E36 - Water collection, treatment and supply
E36.0 - Water collection, treatment and supply
E36.0.0 - Water collection, treatment and supply
E37 - Sewerage
E37.0 - Sewerage
E37.0.0 - Sewerage
E38 - Waste collection, treatment and disposal activities; materials recovery
E38.1 - Waste collection
E38.1.1 - Collection of non-hazardous waste
E38.1.2 - Collection of hazardous waste
E38.2 - Waste treatment and disposal
E38.2.1 - Treatment and disposal of non-hazardous waste
E38.2.2 - Treatment and disposal of hazardous waste
E38.3 - Materials recovery
E38.3.1 - Dismantling of wrecks
E38.3.2 - Recovery of sorted materials
E39 - Remediation activities and other waste management services
E39.0 - Remediation activities and other waste management services
E39.0.0 - Remediation activities and other waste management services
F - Construction
F41 - Construction of buildings
F41.1 - Development of building projects
F41.1.0 - Development of building projects
F41.2 - Construction of residential and non-residential buildings
F41.2.0 - Construction of residential and non-residential buildings
F42 - Civil engineering
F42.1 - Construction of roads and railways
F42.1.1 - Construction of roads and motorways
F42.1.2 - Construction of railways and underground railways
F42.1.3 - Construction of bridges and tunnels
F42.2 - Construction of utility projects
F42.2.1 - Construction of utility projects for fluids
F42.2.2 - Construction of utility projects for electricity and telecommunications
F42.9 - Construction of other civil engineering projects
F42.9.1 - Construction of water projects
F42.9.9 - Construction of other civil engineering projects n.e.c.
F43 - Specialised construction activities
F43.1 - Demolition and site preparation
F43.1.1 - Demolition
F43.1.2 - Site preparation
F43.1.3 - Test drilling and boring
F43.2 - Electrical, plumbing and other construction installation activities
F43.2.1 - Electrical installation
F43.2.2 - Plumbing, heat and air-conditioning installation
F43.2.9 - Other construction installation
F43.3 - Building completion and finishing
F43.3.1 - Plastering
F43.3.2 - Joinery installation
F43.3.3 - Floor and wall covering
F43.3.4 - Painting and glazing
F43.3.9 - Other building completion and finishing
F43.9 - Other specialised construction activities
F43.9.1 - Roofing activities
F43.9.9 - Other specialised construction activities n.e.c.
G - Wholesale and retail trade; repair of motor vehicles and motorcycles
G45 - Wholesale and retail trade and repair of motor vehicles and motorcycles
G45.1 - Sale of motor vehicles
G45.1.1 - Sale of cars and light motor vehicles
G45.1.9 - Sale of other motor vehicles
G45.2 - Maintenance and repair of motor vehicles
G45.2.0 - Maintenance and repair of motor vehicles
G45.3 - Sale of motor vehicle parts and accessories
G45.3.1 - Wholesale trade of motor vehicle parts and accessories
G45.3.2 - Retail trade of motor vehicle parts and accessories
G45.4 - Sale, maintenance and repair of motorcycles and related parts and accessories
G45.4.0 - Sale, maintenance and repair of motorcycles and related parts and accessories
G46 - Wholesale trade, except of motor vehicles and motorcycles
G46.1 - Wholesale on a fee or contract basis
G46.1.1 - Agents involved in the sale of agricultural raw materials, live animals, textile raw materials and semi-finished goods
G46.1.2 - Agents involved in the sale of fuels, ores, metals and industrial chemicals
G46.1.3 - Agents involved in the sale of timber and building materials
G46.1.4 - Agents involved in the sale of machinery, industrial equipment, ships and aircraft
G46.1.5 - Agents involved in the sale of furniture, household goods, hardware and ironmongery
G46.1.6 - Agents involved in the sale of textiles, clothing, fur, footwear and leather goods
G46.1.7 - Agents involved in the sale of food, beverages and tobacco
G46.1.8 - Agents specialised in the sale of other particular products
G46.1.9 - Agents involved in the sale of a variety of goods
G46.2 - Wholesale of agricultural raw materials and live animals
G46.2.1 - Wholesale of grain, unmanufactured tobacco, seeds and animal feeds
G46.2.2 - Wholesale of flowers and plants
G46.2.3 - Wholesale of live animals
G46.2.4 - Wholesale of hides, skins and leather
G46.3 - Wholesale of food, beverages and tobacco
G46.3.1 - Wholesale of fruit and vegetables
G46.3.2 - Wholesale of meat and meat products
G46.3.3 - Wholesale of dairy products, eggs and edible oils and fats
G46.3.4 - Wholesale of beverages
G46.3.5 - Wholesale of tobacco products
G46.3.6 - Wholesale of sugar and chocolate and sugar confectionery
G46.3.7 - Wholesale of coffee, tea, cocoa and spices
G46.3.8 - Wholesale of other food, including fish, crustaceans and molluscs
G46.3.9 - Non-specialised wholesale of food, beverages and tobacco
G46.4 - Wholesale of household goods
G46.4.1 - Wholesale of textiles
G46.4.2 - Wholesale of clothing and footwear
G46.4.3 - Wholesale of electrical household appliances
G46.4.4 - Wholesale of china and glassware and cleaning materials
G46.4.5 - Wholesale of perfume and cosmetics
G46.4.6 - Wholesale of pharmaceutical goods
G46.4.7 - Wholesale of furniture, carpets and lighting equipment
G46.4.8 - Wholesale of watches and jewellery
G46.4.9 - Wholesale of other household goods
G46.5 - Wholesale of information and communication equipment
G46.5.1 - Wholesale of computers, computer peripheral equipment and software
G46.5.2 - Wholesale of electronic and telecommunications equipment and parts
G46.6 - Wholesale of other machinery, equipment and supplies
G46.6.1 - Wholesale of agricultural machinery, equipment and supplies
G46.6.2 - Wholesale of machine tools
G46.6.3 - Wholesale of mining, construction and civil engineering machinery
G46.6.4 - Wholesale of machinery for the textile industry and of sewing and knitting machines
G46.6.5 - Wholesale of office furniture
G46.6.6 - Wholesale of other office machinery and equipment
G46.6.9 - Wholesale of other machinery and equipment
G46.7 - Other specialised wholesale
G46.7.1 - Wholesale of solid, liquid and gaseous fuels and related products
G46.7.2 - Wholesale of metals and metal ores
G46.7.3 - Wholesale of wood, construction materials and sanitary equipment
G46.7.4 - Wholesale of hardware, plumbing and heating equipment and supplies
G46.7.5 - Wholesale of chemical products
G46.7.6 - Wholesale of other intermediate products
G46.7.7 - Wholesale of waste and scrap
G46.9 - Non-specialised wholesale trade
G46.9.0 - Non-specialised wholesale trade
G47 - Retail trade, except of motor vehicles and motorcycles
G47.1 - Retail sale in non-specialised stores
G47.1.1 - Retail sale in non-specialised stores with food, beverages or tobacco predominating
G47.1.9 - Other retail sale in non-specialised stores
G47.2 - Retail sale of food, beverages and tobacco in specialised stores
G47.2.1 - Retail sale of fruit and vegetables in specialised stores
G47.2.2 - Retail sale of meat and meat products in specialised stores
G47.2.3 - Retail sale of fish, crustaceans and molluscs in specialised stores
G47.2.4 - Retail sale of bread, cakes, flour confectionery and sugar confectionery in specialised stores
G47.2.5 - Retail sale of beverages in specialised stores
G47.2.6 - Retail sale of tobacco products in specialised stores
G47.2.9 - Other retail sale of food in specialised stores
G47.3 - Retail sale of automotive fuel in specialised stores
G47.3.0 - Retail sale of automotive fuel in specialised stores
G47.4 - Retail sale of information and communication equipment in specialised stores
G47.4.1 - Retail sale of computers, peripheral units and software in specialised stores
G47.4.2 - Retail sale of telecommunications equipment in specialised stores
G47.4.3 - Retail sale of audio and video equipment in specialised stores
G47.5 - Retail sale of other household equipment in specialised stores
G47.5.1 - Retail sale of textiles in specialised stores
G47.5.2 - Retail sale of hardware, paints and glass in specialised stores
G47.5.3 - Retail sale of carpets, rugs, wall and floor coverings in specialised stores
G47.5.4 - Retail sale of electrical household appliances in specialised stores
G47.5.9 - Retail sale of furniture, lighting equipment and other household articles in specialised stores
G47.6 - Retail sale of cultural and recreation goods in specialised stores
G47.6.1 - Retail sale of books in specialised stores
G47.6.2 - Retail sale of newspapers and stationery in specialised stores
G47.6.3 - Retail sale of music and video recordings in specialised stores
G47.6.4 - Retail sale of sporting equipment in specialised stores
G47.6.5 - Retail sale of games and toys in specialised stores
G47.7 - Retail sale of other goods in specialised stores
G47.7.1 - Retail sale of clothing in specialised stores
G47.7.2 - Retail sale of footwear and leather goods in specialised stores
G47.7.3 - Dispensing chemist in specialised stores
G47.7.4 - Retail sale of medical and orthopaedic goods in specialised stores
G47.7.5 - Retail sale of cosmetic and toilet articles in specialised stores
G47.7.6 - Retail sale of flowers, plants, seeds, fertilisers, pet animals and pet food in specialised stores
G47.7.7 - Retail sale of watches and jewellery in specialised stores
G47.7.8 - Other retail sale of new goods in specialised stores
G47.7.9 - Retail sale of second-hand goods in stores
G47.8 - Retail sale via stalls and markets
G47.8.1 - Retail sale via stalls and markets of food, beverages and tobacco products
G47.8.2 - Retail sale via stalls and markets of textiles, clothing and footwear
G47.8.9 - Retail sale via stalls and markets of other goods
G47.9 - Retail trade not in stores, stalls or markets
G47.9.1 - Retail sale via mail order houses or via Internet
G47.9.9 - Other retail sale not in stores, stalls or markets
H - Transporting and storage
H49 - Land transport and transport via pipelines
H49.1 - Passenger rail transport, interurban
H49.1.0 - Passenger rail transport, interurban
H49.2 - Freight rail transport
H49.2.0 - Freight rail transport
H49.3 - Other passenger land transport
H49.3.1 - Urban and suburban passenger land transport
H49.3.2 - Taxi operation
H49.3.9 - Other passenger land transport n.e.c.
H49.4 - Freight transport by road and removal services
H49.4.1 - Freight transport by road
H49.4.2 - Removal services
H49.5 - Transport via pipeline
H49.5.0 - Transport via pipeline
H50 - Water transport
H50.1 - Sea and coastal passenger water transport
H50.1.0 - Sea and coastal passenger water transport
H50.2 - Sea and coastal freight water transport
H50.2.0 - Sea and coastal freight water transport
H50.3 - Inland passenger water transport
H50.3.0 - Inland passenger water transport
H50.4 - Inland freight water transport
H50.4.0 - Inland freight water transport
H51 - Air transport
H51.1 - Passenger air transport
H51.1.0 - Passenger air transport
H51.2 - Freight air transport and space transport
H51.2.1 - Freight air transport
H51.2.2 - Space transport
H52 - Warehousing and support activities for transportation
H52.1 - Warehousing and storage
H52.1.0 - Warehousing and storage
H52.2 - Support activities for transportation
H52.2.1 - Service activities incidental to land transportation
H52.2.2 - Service activities incidental to water transportation
H52.2.3 - Service activities incidental to air transportation
H52.2.4 - Cargo handling
H52.2.9 - Other transportation support activities
H53 - Postal and courier activities
H53.1 - Postal activities under universal service obligation
H53.1.0 - Postal activities under universal service obligation
H53.2 - Other postal and courier activities
H53.2.0 - Other postal and courier activities
I - Accommodation and food service activities
I55 - Accommodation
I55.1 - Hotels and similar accommodation
I55.1.0 - Hotels and similar accommodation
I55.2 - Holiday and other short-stay accommodation
I55.2.0 - Holiday and other short-stay accommodation
I55.3 - Camping grounds, recreational vehicle parks and trailer parks
I55.3.0 - Camping grounds, recreational vehicle parks and trailer parks
I55.9 - Other accommodation
I55.9.0 - Other accommodation
I56 - Food and beverage service activities
I56.1 - Restaurants and mobile food service activities
I56.1.0 - Restaurants and mobile food service activities
I56.2 - Event catering and other food service activities
I56.2.1 - Event catering activities
I56.2.9 - Other food service activities
I56.3 - Beverage serving activities
I56.3.0 - Beverage serving activities
J - Information and communication
J58 - Publishing activities
J58.1 - Publishing of books, periodicals and other publishing activities
J58.1.1 - Book publishing
J58.1.2 - Publishing of directories and mailing lists
J58.1.3 - Publishing of newspapers
J58.1.4 - Publishing of journals and periodicals
J58.1.9 - Other publishing activities
J58.2 - Software publishing
J58.2.1 - Publishing of computer games
J58.2.9 - Other software publishing
J59 - Motion picture, video and television programme production, sound recording and music publishing activities
J59.1 - Motion picture, video and television programme activities
J59.1.1 - Motion picture, video and television programme production activities
J59.1.2 - Motion picture, video and television programme post-production activities
J59.1.3 - Motion picture, video and television programme distribution activities
J59.1.4 - Motion picture projection activities
J59.2 - Sound recording and music publishing activities
J59.2.0 - Sound recording and music publishing activities
J60 - Programming and broadcasting activities
J60.1 - Radio broadcasting
J60.1.0 - Radio broadcasting
J60.2 - Television programming and broadcasting activities
J60.2.0 - Television programming and broadcasting activities
J61 - Telecommunications
J61.1 - Wired telecommunications activities
J61.1.0 - Wired telecommunications activities
J61.2 - Wireless telecommunications activities
J61.2.0 - Wireless telecommunications activities
J61.3 - Satellite telecommunications activities
J61.3.0 - Satellite telecommunications activities
J61.9 - Other telecommunications activities
J61.9.0 - Other telecommunications activities
J62 - Computer programming, consultancy and related activities
J62.0 - Computer programming, consultancy and related activities
J62.0.1 - Computer programming activities
J62.0.2 - Computer consultancy activities
J62.0.3 - Computer facilities management activities
J62.0.9 - Other information technology and computer service activities
J63 - Information service activities
J63.1 - Data processing, hosting and related activities; web portals
J63.1.1 - Data processing, hosting and related activities
J63.1.2 - Web portals
J63.9 - Other information service activities
J63.9.1 - News agency activities
J63.9.9 - Other information service activities n.e.c.
K - Financial and insurance activities
K64 - Financial service activities, except insurance and pension funding
K64.1 - Monetary intermediation
K64.1.1 - Central banking
K64.1.9 - Other monetary intermediation
K64.2 - Activities of holding companies
K64.2.0 - Activities of holding companies
K64.3 - Trusts, funds and similar financial entities
K64.3.0 - Trusts, funds and similar financial entities
K64.9 - Other financial service activities, except insurance and pension funding
K64.9.1 - Financial leasing
K64.9.2 - Other credit granting
K64.9.9 - Other financial service activities, except insurance and pension funding n.e.c.
K65 - Insurance, reinsurance and pension funding, except compulsory social security
K65.1 - Insurance
K65.1.1 - Life insurance
K65.1.2 - Non-life insurance
K65.2 - Reinsurance
K65.2.0 - Reinsurance
K65.3 - Pension funding
K65.3.0 - Pension funding
K66 - Activities auxiliary to financial services and insurance activities
K66.1 - Activities auxiliary to financial services, except insurance and pension funding
K66.1.1 - Administration of financial markets
K66.1.2 - Security and commodity contracts brokerage
K66.1.9 - Other activities auxiliary to financial services, except insurance and pension funding
K66.2 - Activities auxiliary to insurance and pension funding
K66.2.1 - Risk and damage evaluation
K66.2.2 - Activities of insurance agents and brokers
K66.2.9 - Other activities auxiliary to insurance and pension funding
K66.3 - Fund management activities
K66.3.0 - Fund management activities
L - Real estate activities
L68 - Real estate activities
L68.1 - Buying and selling of own real estate
L68.1.0 - Buying and selling of own real estate
L68.2 - Renting and operating of own or leased real estate
L68.2.0 - Renting and operating of own or leased real estate
L68.3 - Real estate activities on a fee or contract basis
L68.3.1 - Real estate agencies
L68.3.2 - Management of real estate on a fee or contract basis
M - Professional, scientific and technical activities
M69 - Legal and accounting activities
M69.1 - Legal activities
M69.1.0 - Legal activities
M69.2 - Accounting, bookkeeping and auditing activities; tax consultancy
M69.2.0 - Accounting, bookkeeping and auditing activities; tax consultancy
M70 - Activities of head offices; management consultancy activities
M70.1 - Activities of head offices
M70.1.0 - Activities of head offices
M70.2 - Management consultancy activities
M70.2.1 - Public relations and communication activities
M70.2.2 - Business and other management consultancy activities
M71 - Architectural and engineering activities; technical testing and analysis
M71.1 - Architectural and engineering activities and related technical consultancy
M71.1.1 - Architectural activities
M71.1.2 - Engineering activities and related technical consultancy
M71.2 - Technical testing and analysis
M71.2.0 - Technical testing and analysis
M72 - Scientific research and development
M72.1 - Research and experimental development on natural sciences and engineering
M72.1.1 - Research and experimental development on biotechnology
M72.1.9 - Other research and experimental development on natural sciences and engineering
M72.2 - Research and experimental development on social sciences and humanities
M72.2.0 - Research and experimental development on social sciences and humanities
M73 - Advertising and market research
M73.1 - Advertising
M73.1.1 - Advertising agencies
M73.1.2 - Media representation
M73.2 - Market research and public opinion polling
M73.2.0 - Market research and public opinion polling
M74 - Other professional, scientific and technical activities
M74.1 - Specialised design activities
M74.1.0 - Specialised design activities
M74.2 - Photographic activities
M74.2.0 - Photographic activities
M74.3 - Translation and interpretation activities
M74.3.0 - Translation and interpretation activities
M74.9 - Other professional, scientific and technical activities n.e.c.
M74.9.0 - Other professional, scientific and technical activities n.e.c.
M75 - Veterinary activities
M75.0 - Veterinary activities
M75.0.0 - Veterinary activities
N - Administrative and support service activities
N77 - Rental and leasing activities
N77.1 - Renting and leasing of motor vehicles
N77.1.1 - Renting and leasing of cars and light motor vehicles
N77.1.2 - Renting and leasing of trucks
N77.2 - Renting and leasing of personal and household goods
N77.2.1 - Renting and leasing of recreational and sports goods
N77.2.2 - Renting of video tapes and disks
N77.2.9 - Renting and leasing of other personal and household goods
N77.3 - Renting and leasing of other machinery, equipment and tangible goods
N77.3.1 - Renting and leasing of agricultural machinery and equipment
N77.3.2 - Renting and leasing of construction and civil engineering machinery and equipment
N77.3.3 - Renting and leasing of office machinery and equipment (including computers)
N77.3.4 - Renting and leasing of water transport equipment
N77.3.5 - Renting and leasing of air transport equipment
N77.3.9 - Renting and leasing of other machinery, equipment and tangible goods n.e.c.
N77.4 - Leasing of intellectual property and similar products, except copyrighted works
N77.4.0 - Leasing of intellectual property and similar products, except copyrighted works
N78 - Employment activities
N78.1 - Activities of employment placement agencies
N78.1.0 - Activities of employment placement agencies
N78.2 - Temporary employment agency activities
N78.2.0 - Temporary employment agency activities
N78.3 - Other human resources provision
N78.3.0 - Other human resources provision
N79 - Travel agency, tour operator and other reservation service and related activities
N79.1 - Travel agency and tour operator activities
N79.1.1 - Travel agency activities
N79.1.2 - Tour operator activities
N79.9 - Other reservation service and related activities
N79.9.0 - Other reservation service and related activities
N80 - Security and investigation activities
N80.1 - Private security activities
N80.1.0 - Private security activities
N80.2 - Security systems service activities
N80.2.0 - Security systems service activities
N80.3 - Investigation activities
N80.3.0 - Investigation activities
N81 - Services to buildings and landscape activities
N81.1 - Combined facilities support activities
N81.1.0 - Combined facilities support activities
N81.2 - Cleaning activities
N81.2.1 - General cleaning of buildings
N81.2.2 - Other building and industrial cleaning activities
N81.2.9 - Other cleaning activities
N81.3 - Landscape service activities
N81.3.0 - Landscape service activities
N82 - Office administrative, office support and other business support activities
N82.1 - Office administrative and support activities
N82.1.1 - Combined office administrative service activities
N82.1.9 - Photocopying, document preparation and other specialised office support activities
N82.2 - Activities of call centres
N82.2.0 - Activities of call centres
N82.3 - Organisation of conventions and trade shows
N82.3.0 - Organisation of conventions and trade shows
N82.9 - Business support service activities n.e.c.
N82.9.1 - Activities of collection agencies and credit bureaus
N82.9.2 - Packaging activities
N82.9.9 - Other business support service activities n.e.c.
O - Public administration and defence; compulsory social security
O84 - Public administration and defence; compulsory social security
O84.1 - Administration of the State and the economic and social policy of the community
O84.1.1 - General public administration activities
O84.1.2 - Regulation of the activities of providing health care, education, cultural services and other social services, excluding social security
O84.1.3 - Regulation of and contribution to more efficient operation of businesses
O84.2 - Provision of services to the community as a whole
O84.2.1 - Foreign affairs
O84.2.2 - Defence activities
O84.2.3 - Justice and judicial activities
O84.2.4 - Public order and safety activities
O84.2.5 - Fire service activities
O84.3 - Compulsory social security activities
O84.3.0 - Compulsory social security activities
P - Education
P85 - Education
P85.1 - Pre-primary education
P85.1.0 - Pre-primary education
P85.2 - Primary education
P85.2.0 - Primary education
P85.3 - Secondary education
P85.3.1 - General secondary education
P85.3.2 - Technical and vocational secondary education
P85.4 - Higher education
P85.4.1 - Post-secondary non-tertiary education
P85.4.2 - Tertiary education
P85.5 - Other education
P85.5.1 - Sports and recreation education
P85.5.2 - Cultural education
P85.5.3 - Driving school activities
P85.5.9 - Other education n.e.c.
P85.6 - Educational support activities
P85.6.0 - Educational support activities
Q - Human health and social work activities
Q86 - Human health activities
Q86.1 - Hospital activities
Q86.1.0 - Hospital activities
Q86.2 - Medical and dental practice activities
Q86.2.1 - General medical practice activities
Q86.2.2 - Specialist medical practice activities
Q86.2.3 - Dental practice activities
Q86.9 - Other human health activities
Q86.9.0 - Other human health activities
Q87 - Residential care activities
Q87.1 - Residential nursing care activities
Q87.1.0 - Residential nursing care activities
Q87.2 - Residential care activities for mental retardation, mental health and substance abuse
Q87.2.0 - Residential care activities for mental retardation, mental health and substance abuse
Q87.3 - Residential care activities for the elderly and disabled
Q87.3.0 - Residential care activities for the elderly and disabled
Q87.9 - Other residential care activities
Q87.9.0 - Other residential care activities
Q88 - Social work activities without accommodation
Q88.1 - Social work activities without accommodation for the elderly and disabled
Q88.1.0 - Social work activities without accommodation for the elderly and disabled
Q88.9 - Other social work activities without accommodation
Q88.9.1 - Child day-care activities
Q88.9.9 - Other social work activities without accommodation n.e.c.
R - Arts, entertainment and recreation
R90 - Creative, arts and entertainment activities
R90.0 - Creative, arts and entertainment activities
R90.0.1 - Performing arts
R90.0.2 - Support activities to performing arts
R90.0.3 - Artistic creation
R90.0.4 - Operation of arts facilities
R91 - Libraries, archives, museums and other cultural activities
R91.0 - Libraries, archives, museums and other cultural activities
R91.0.1 - Library and archives activities
R91.0.2 - Museums activities
R91.0.3 - Operation of historical sites and buildings and similar visitor attractions
R91.0.4 - Botanical and zoological gardens and nature reserves activities
R92 - Gambling and betting activities
R92.0 - Gambling and betting activities
R92.0.0 - Gambling and betting activities
R93 - Sports activities and amusement and recreation activities
R93.1 - Sports activities
R93.1.1 - Operation of sports facilities
R93.1.2 - Activities of sport clubs
R93.1.3 - Fitness facilities
R93.1.9 - Other sports activities
R93.2 - Amusement and recreation activities
R93.2.1 - Activities of amusement parks and theme parks
R93.2.9 - Other amusement and recreation activities
S - Other services activities
S94 - Activities of membership organisations
S94.1 - Activities of business, employers and professional membership organisations
S94.1.1 - Activities of business and employers membership organisations
S94.1.2 - Activities of professional membership organisations
S94.2 - Activities of trade unions
S94.2.0 - Activities of trade unions
S94.9 - Activities of other membership organisations
S94.9.1 - Activities of religious organisations
S94.9.2 - Activities of political organisations
S94.9.9 - Activities of other membership organisations n.e.c.
S95 - Repair of computers and personal and household goods
S95.1 - Repair of computers and communication equipment
S95.1.1 - Repair of computers and peripheral equipment
S95.1.2 - Repair of communication equipment
S95.2 - Repair of personal and household goods
S95.2.1 - Repair of consumer electronics
S95.2.2 - Repair of household appliances and home and garden equipment
S95.2.3 - Repair of footwear and leather goods
S95.2.4 - Repair of furniture and home furnishings
S95.2.5 - Repair of watches, clocks and jewellery
S95.2.9 - Repair of other personal and household goods
S96 - Other personal service activities
S96.0 - Other personal service activities
S96.0.1 - Washing and (dry-)cleaning of textile and fur products
S96.0.2 - Hairdressing and other beauty treatment
S96.0.3 - Funeral and related activities
S96.0.4 - Physical well-being activities
S96.0.9 - Other personal service activities n.e.c.
T - Activities of households as employers; undifferentiated goods - and services - producing activities of households for own use
T97 - Activities of households as employers of domestic personnel
T97.0 - Activities of households as employers of domestic personnel
T97.0.0 - Activities of households as employers of domestic personnel
T98 - Undifferentiated goods- and services-producing activities of private households for own use
T98.1 - Undifferentiated goods-producing activities of private households for own use
T98.1.0 - Undifferentiated goods-producing activities of private households for own use
T98.2 - Undifferentiated service-producing activities of private households for own use
T98.2.0 - Undifferentiated service-producing activities of private households for own use
U - Activities of extraterritorial organisations and bodies
U99 - Activities of extraterritorial organisations and bodies
U99.0 - Activities of extraterritorial organisations and bodies
U99.0.0 - Activities of extraterritorial organisations and bodies
"""

nace_data_dutch = """
A - Land- und Forstwirtschaft, Fischerei
A1 - Pflanzenbau, Tierproduktion, Jagd und damit verbundene Dienstleistungen
A1.1 - Anbau einjähriger Pflanzen
A1.1.1 - Anbau von Getreide (ohne Reis), Hülsenfrüchten und Ölsaaten
A1.1.2 - Anbau von Reis
A1.1.3 - Anbau von Gemüse und Melonen, Wurzeln und Knollen
A1.1.4 - Anbau von Zuckerrohr
A1.1.5 - Anbau von Tabak
A1.1.6 - Anbau von Faserpflanzen
A1.1.9 - Anbau anderer einjähriger Pflanzen
A1.2 - Anbau mehrjähriger Pflanzen
A1.2.1 - Anbau von Weintrauben
A1.2.2 - Anbau tropischer und subtropischer Früchte
A1.2.3 - Anbau von Zitrusfrüchten
A1.2.4 - Anbau von Kern- und Steinobst
A1.2.5 - Anbau von sonstige Baum- und Strauchfrüchte und Nüsse
A1.2.6 - Anbau von Ölfrüchten
A1.2.7 - Anbau von Getränkepflanzen
A1.2.8 - Anbau von Gewürzen, aromatischen Pflanzen, Drogen und pharmazeutischen Pflanzen
A1.2.9 - Anbau sonstiger mehrjähriger Pflanzen
A1.3 - Pflanzenvermehrung
A1.3.0 - Pflanzenvermehrung
A1.4 - Tierproduktion
A1.4.1 - Milchviehhaltung
A1.4.2 - Haltung sonstiger Rinder und Büffel
A1.4.3 - Haltung von Pferden und anderen Einhufern
A1.4.4 - Haltung von Kamelen und Kamelartigen
A1.4.5 - Haltung von Schafen und Ziegen
A1.4.6 - Haltung von Schweinen
A1.4.7 - Haltung von Geflügel
A1.4.9 - Haltung sonstiger Tiere
A1.5 - Gemischte Landwirtschaft
A1.5.0 - Gemischte Landwirtschaft
A1.6 - Unterstützende Tätigkeiten für die Landwirtschaft und Nacherntefrüchte Tätigkeiten
A1.6.1 - Unterstützende Tätigkeiten für die Pflanzenproduktion
A1.6.2 - Unterstützende Tätigkeiten für die Tierproduktion
A1.6.3 - Nacherntetätigkeiten für Pflanzen
A1.6.4 - Saatgutaufbereitung für Vermehrungszwecke
A1.7 - Jagd, Fallenstellerei und damit verbundene Tätigkeiten
A1.7.0 - Jagd, Fallenstellerei und damit verbundene Tätigkeiten
A2 - Forstwirtschaft und Holzeinschlag
A2.1 - Forstwirtschaft und sonstige forstwirtschaftliche Tätigkeiten
A2.1.0 - Forstwirtschaft und sonstige forstwirtschaftliche Tätigkeiten
A2.2 - Holzeinschlag
A2.2.0 - Holzeinschlag
A2.3 - Sammeln von wild wachsenden Nichtholzprodukten
A2.3.0 - Sammeln von wild wachsenden Nichtholzprodukten
A2.4 - Unterstützende Dienste für die Forstwirtschaft
A2.4.0 - Unterstützende Dienste für die Forstwirtschaft
A3 - Fischerei und Aquakultur
A3.1 - Fischerei
A3.1.1 - Meeresfischerei
A3.1.2 - Süßwasserfischerei
A3.2 - Aquakultur
A3.2.1 - Meeresaquakultur
A3.2.2 - Süßwasseraquakultur
B - Bergbau und Gewinnung von Steinen und Erden 
B5 - Kohlebergbau 
B5.1 - Steinkohlebergbau
B5.1.0 - Steinkohlebergbau
B5.2 - Braunkohlebergbau
B5.2.0 - Braunkohlebergbau
B6 - Gewinnung von Erdöl und Erdgas
B6.1 - Gewinnung von Erdöl
B6.1.0 - Gewinnung von Erdöl
B6.2 - Gewinnung von Erdgas 
B6.2.0 - Gewinnung von Erdgas
B7 - Erzbergbau 
B7.1 - Eisenerzbergbau 
B7.1.0 - Eisenerzbergbau 
B7.2 - Nichteisenmetallerzbergbau 
B7.2.1 - Uran- und Thoriumerzbergbau 
B7.2.9 - Bergbau auf sonstige Nichteisenmetallerze 
B8 - Sonstiger Bergbau und Gewinnung von Steinen und Erden 
B8.1 - Gewinnung von Natursteinen, Sand und Ton 
B8.1.1 - Gewinnung von Schmuck- und Bausteinen, Kalkstein, Gips, Kreide und Schiefer 
B8.1.2 - Betrieb von Kies- und Sandgruben; Ton- und Kaolinabbau 
B8.9 - Bergbau und Gewinnung von Steinen und Erden a. g. 
B8.9.1 - Bergbau auf chemische und Düngemittelmineralien 
B8.9.2 - Torfgewinnung 
B8.9.3 - Salzgewinnung 
B8.9.9 - Sonstiger Bergbau und Gewinnung von Steinen und Erden a. g. 
B9 - Erbringung von unterstützenden Dienstleistungen für den Bergbau 
B9.1 - Erbringung von unterstützenden Dienstleistungen für die Erdöl- und Erdgasförderung 
B9.1.0 - Erbringung von unterstützenden Dienstleistungen für die Erdöl- und Erdgasförderung 
B9.9 - Erbringung von sonstigen Bergbauleistungen und Gewinnung von Steinen und Erden a. g. 
B9.9.0 - Erbringung von sonstigen Bergbauleistungen und Gewinnung von Steinen und Erden a. g. 
C - Verarbeitendes Gewerbe
C10 - Herstellung von Nahrungsmitteln
C10.1 - Fleischverarbeitung und -konservierung und Herstellung von Fleischerzeugnissen
C10.1.1 - Fleischverarbeitung und -konservierung
C10.1.2 - Geflügelfleischverarbeitung und -konservierung
C10.1.3 - Herstellung von Fleisch
C10.2.0 - Verarbeitung und Konservierung von Fischen, Krebs- und Weichtieren
C10.3 - Verarbeitung und Konservierung von Obst und Gemüse
C10.3.1 - Verarbeitung und Konservierung von Kartoffeln
C10.3.2 - Herstellung von Frucht- und Gemüsesäften
C10.3.9 - Sonstige Verarbeitung und Konservierung von Obst und Gemüse
C10.4 - Herstellung von pflanzlichen und tierischen Ölen und Fetten
C10.4.1 - Herstellung von Ölen und Fetten
C10.4.2 - Herstellung von Margarine und ähnlichen Speisefetten
C10.5 - Herstellung von Molkereiprodukten
C10.5.1 - Betrieb von Molkereien und Käsereien
C10.5.2 - Herstellung von Speiseeis
C10.6 - Herstellung von Mahlprodukten, Stärke und Stärkeerzeugnissen
C10.6.1 - Herstellung von Mahlprodukten
C10.6.2 - Herstellung von Stärke und Stärkeerzeugnissen
C10.7 - Herstellung von Back- und Mehlwaren
C10.7.1 - Herstellung von Brot; Herstellung von frischen Backwaren und Kuchen
C10.7.2 - Herstellung von Zwieback und Keksen; Herstellung von haltbar gemachten Backwaren und Kuchen
C10.7.3 - Herstellung von Makkaroni, Nudeln, Couscous und ähnlichen mehlhaltigen Erzeugnissen
C10.8 - Herstellung von sonstigen Nahrungsmitteln
C10.8.1 - Herstellung von Zucker
C10.8.2 - Herstellung von Kakao, Schokolade und Zuckerwaren
C10.8.3 - Verarbeitung von Tee und Kaffee
C10.8.4 - Herstellung von Würzmitteln und Gewürzen
C10.8.5 - Herstellung von Fertiggerichten und Speisen
C10.8.6 - Herstellung von homogenisierten Lebensmittelzubereitungen und diätetischen Lebensmitteln
C10.8.9 - Herstellung von sonstigen Nahrungsmitteln ang 
C10.9 - Herstellung von zubereitetem Tierfutter
C10.9.1 - Herstellung von Fertigfutter für Nutztiere
C10.9.2 - Herstellung von zubereitetem Heimtierfutter
C11 - Herstellung von Getränken
C11.0 - Herstellung von Getränken
C11.0.1 - Destillieren, Rektifizieren und Mischen von Spirituosen
C11.0.2 - Herstellung von Wein aus Trauben
C11.0.3 - Herstellung von Apfelwein und anderen Fruchtweinen
C11.0.4 - Herstellung von sonstigen nicht destillierten gegorenen Getränken
C11.0.5 - Herstellung von Bier
C11.0.6 - Herstellung von Malz
C11.0.7 - Herstellung von alkoholfreien Getränken; Herstellung von Mineralwasser und anderen abgefüllten Wässern
C12 - Herstellung von Tabakwaren
C12.0 - Herstellung von Tabakwaren
C12.0.0 - Herstellung von Tabakwaren
C13 - Herstellung von Textilien
C13.1 - Textilfaseraufbereitung und -spinnerei
C13.1.0 - Textilfaseraufbereitung und -spinnerei 
C13.2 - Weberei von Textilien
C13.2.0 - Weberei von Textilien
C13.3 - Textilveredelung
C13.3.0 - Textilveredelung
C13.9 - Herstellung von sonstigen Textilien
C13.9.1 - Herstellung von gewirktem und gestricktem Stoff
C13.9.2 - Herstellung von konfektionierten Textilwaren (ohne Bekleidung)
C13.9.3 - Herstellung von Teppichen
C13.9.4 - Herstellung von Tauen, Seilen, Bindfäden und Netzen
C13.9.5 - Herstellung von Vliesstoffen und Waren aus Vliesstoffen (ausgenommen Bekleidung)
C13.9.6 - Herstellung von sonstigen technischen und industriellen Textilien
C13.9.9 - Herstellung von sonstigen Textilien ang
C14 - Herstellung von Bekleidung
C14.1 - Herstellung von Bekleidung (ausgenommen Pelzbekleidung)
C14.1.1 - Herstellung von Lederbekleidung
C14.1.2 - Herstellung von Arbeitskleidung
C14.1.3 - Herstellung von sonstiger Oberbekleidung
C14.1.4 - Herstellung von Unterwäsche
C14.1.9 - Herstellung von sonstiger Bekleidung und Zubehör
C14.2 - Herstellung von Pelzwaren
C14.2.0 - Herstellung von Pelzwaren
C14.3 - Herstellung von gewirkter und gehäkelter Bekleidung
C14.3.1 - Herstellung von Strumpfwaren
C14.3.9 - Herstellung von sonstiger gewirkter und gehäkelter Bekleidung
C15 - Herstellung von Leder und verwandten Produkten
C15.1 - Gerben und Zurichtung von Leder; Herstellung von Reisegepäck, Handtaschen, Sattlerwaren und Geschirren; Zurichtung und Färben von Pelzen
C15.1.1 - Gerben und Zurichtung von Leder; Zurichtung und Färben von Pelzen
C15.1.2 - Herstellung von Reisegepäck, Handtaschen und dergleichen, Sattlerwaren und Geschirren
C15.2 - Herstellung von Schuhen
C15.2.0 - Herstellung von Schuhen
C16 - Herstellung von Holz und von Produkten aus Holz und Kork (ausgenommen Möbel); Herstellung von Waren aus Stroh und Flechtstoffen
C16.1 - Säge- und Hobelarbeiten von Holz
C16.1.0 - Säge- und Hobelarbeiten von Holz
C16.2 - Herstellung von Waren aus Holz, Kork, Stroh und Flechtstoffen
C16.2.1 - Herstellung von Furnierblättern und Holzwerkstoffen
C16.2.2 - Herstellung von Fertigparkett
C16.2.3 - Herstellung von sonstigen Bautischlerei- und Zimmereiarbeiten
C16.2.4 - Herstellung von Holzbehältern
C16.2.9 - Herstellung von sonstigen Produkten aus Holz; Herstellung von Waren aus Kork, Stroh und Flechtstoffen
C17 - Herstellung von Papier und Papierwaren
C17.1 - Herstellung von Zellstoff, Papier und Pappe
C17.1.1 - Herstellung von Zellstoff
C17.1.2 - Herstellung von Papier und Pappe
C17.2 - Herstellung von Waren aus Papier und Pappe
C17.2.1 - Herstellung von Wellpapier und Wellpappe und von Behältern aus Papier und Pappe
C17.2.2 - Herstellung von Haushalts- und Hygieneartikeln sowie von Toilettenartikeln
C17.2.3 - Herstellung von Schreibwaren aus Papier
C17.2.4 - Herstellung von Tapeten
C17.2.9 - Herstellung von sonstigen Waren aus Papier und Pappe
C18 - Drucken und Vervielfältigen von bespielten Datenträgern
C18.1 - Druckerei- und Dienstleistungstätigkeiten im Zusammenhang mit dem Drucken
C18.1.1 - Drucken von Zeitungen
C18.1.2 - Sonstige Druckereidienstleistungen
C18.1.3 - Druckvorstufe und Medienvorstufe
C18.1.4 - Buchbinderei und damit verbundene Dienstleistungen
C18.2 - Vervielfältigen von bespielten Datenträgern 
C18.2.0 - Vervielfältigen von bespielten Datenträgern
C19 - Herstellung von Kokerei- und Mineralölerzeugnissen
C19.1 - Herstellung von Kokereierzeugnissen
C19.1.0 - Herstellung von Kokereierzeugnissen 
C19.2 - Herstellung von Mineralölerzeugnissen
C19.2.0 - Herstellung von Mineralölerzeugnissen
C20 - Herstellung von Chemikalien und chemischen Erzeugnissen
C20.1 - Herstellung von chemischen Grundstoffen, Düngemitteln und Stickstoffverbindungen, Kunststoffen und synthetischem Kautschuk in Primärformen
C20.1.1 - Herstellung von Industriegasen
C20.1.2 - Herstellung von Pigmente
C20.1.3 - Herstellung von sonstigen anorganischen Grundstoffen
C20.1.4 - Herstellung von sonstigen organischen Grundstoffen
C20.1.5 - Herstellung von Düngemitteln und Stickstoffverbindungen
C20.1.6 - Herstellung von Kunststoffen in Primärformen
C20.1.7 - Herstellung von synthetischem Kautschuk in Primärformen
C20.2 - Herstellung von Pestiziden und sonstigen Agrochemikalien
C20.2.0 - Herstellung von Pestiziden und sonstigen Agrochemikalien
C20.3 - Herstellung von Farben, Lacken und ähnlichen Überzügen, Druckfarben und Kitten
C20.3.0 - Herstellung von Farben, Lacken und ähnlichen Überzügen, Druckfarben und Kitten
C20.4 - Herstellung von Seifen und Waschmitteln, Reinigungs- und Poliermitteln, Parfüms und Körperpflegemitteln
C20.4.1 - Herstellung von Seifen und Waschmitteln, Reinigungs- und Poliermitteln
C20.4.2 - Herstellung von Parfüms und Körperpflegemitteln
C20.5 - Herstellung von sonstigen chemischen Erzeugnissen
C20.5.1 - Herstellung von Explosivstoffen
C20.5.2 - Herstellung von Klebstoffen
C20.5.3 - Herstellung von ätherischen Ölen
C20.5.9 - Herstellung von sonstigen chemischen Erzeugnissen ang
C20.6 - Herstellung von Chemiefasern
C20.6.0 - Herstellung von Chemiefasern
C21 - Herstellung von pharmazeutischen Grundstoffen und pharmazeutischen Präparaten
C21.1 - Herstellung von pharmazeutischen Grundstoffen
C21.1.0 - Herstellung von pharmazeutischen Grundstoffen
C21.2 - Herstellung von pharmazeutischen Präparaten
C21.2.0 - Herstellung von pharmazeutischen Erzeugnissen
C22 - Herstellung von Gummi- und Kunststoffwaren
C22.1 - Herstellung von Gummiwaren
C22.1.1 - Herstellung von Gummireifen und -schläuchen; Runderneuerung und Erneuerung von Gummireifen
C22.1.9 - Herstellung von sonstigen Gummiwaren
C22.2 - Herstellung von Kunststoffwaren
C22.2.1 - Herstellung von Platten, Folien, Schläuchen und Profilen aus Kunststoff
C22.2.2 - Herstellung von Verpackungsmaterial aus Kunststoff
C22.2.3 - Herstellung von Baubedarfsartikeln aus Kunststoff
C22.2.9 - Herstellung von sonstigen Kunststoffwaren
C23 - Herstellung von sonstigen Erzeugnissen aus nichtmetallischen Mineralien
C23.1 - Herstellung von Glas und Glaswaren
C23.1.1 - Herstellung von Flachglas
C23.1.2 - Formgebung und Bearbeitung von Flachglas
C23.1.3 - Herstellung von Hohlglas
C23.1.4 - Herstellung von Glasfasern
C23.1.9 - Herstellung und Bearbeitung von sonstigem Glas, einschließlich technischer Glaswaren
C23.2 - Herstellung von feuerfesten Erzeugnissen
C23.2.0 - Herstellung von feuerfesten Erzeugnissen
C23.3 - Herstellung von keramischen Baustoffen
C23.3.1 - Herstellung von keramischen Fliesen und Platten
C23.3.2 - Herstellung von Ziegeln, Fliesen und Bauprodukten aus gebranntem Ton
C23.4 - Herstellung von sonstigen Porzellan- und Keramikwaren
C23.4.1 - Herstellung von keramischen Haushalts- und Ziergegenständen
C23.4.2 - Herstellung von keramischen Sanitärgegenständen
C23.4.3 - Herstellung von keramischen Isolatoren und Isolierstücken
C23.4.4 - Herstellung von sonstigen technischen Keramikwaren
C23.4.9 - Herstellung von sonstigen keramischen Waren
C23.5 - Herstellung von Zement, Kalk und Gips
C23.5.1 - Herstellung von Zement
C23.5.2 - Herstellung von Kalk und Gips
C23.6 - Herstellung von Waren aus Beton, Zement und Gips
C23.6.1 - Herstellung von Betonwaren für Bauzwecke
C23.6.2 - Herstellung von Gipswaren für Bauzwecke
C23.6.3 - Herstellung von Transportbeton
C23.6.4 - Herstellung von Mörtel
C23.6.5 - Herstellung von Faserzement
C23.6.9 - Herstellung von sonstigen Waren aus Beton, Gips und Zement
C23.7 - Schneiden, Bearbeiten und Veredeln von Steinen
C23.7.0 - Schneiden, Bearbeiten und Veredeln von Steinen
C23.9 - Herstellung von Schleifmitteln und Produkten aus nichtmetallischen Mineralien, ang
C23.9.1 - Herstellung von Schleifmitteln
C23.9.9 - Herstellung von sonstigen nichtmetallischen Mineralprodukten ang
C24 - Metallerzeugung und -verarbeitung
C24.1 - Erzeugung von Roheisen, Stahl und Ferrolegierungen
C24.1.0 - Erzeugung von Roheisen, Stahl und Ferrolegierungen
C24.2 - Herstellung von Rohren, Hohlprofilen und entsprechenden Formstücken aus Stahl
C24.2.0 - Herstellung von Rohren, Hohlprofilen und entsprechenden Formstücken aus Stahl
C24.3 - Herstellung von sonstigen Erzeugnissen aus der Erstbearbeitung von Stahl
C24.3.1 - Kaltziehen von Stangen
C24.3.2 - Kaltwalzen von Schmalbändern
C24.3.3 - Kaltverformen oder Abkanten
C24.3.4 - Kaltziehen von Draht
C24.4 - Erzeugung von Edelmetallen und sonstigen Nichteisenmetallen
C24.4.1 - Erzeugung von Edelmetallen
C24.4.2 - Erzeugung von Aluminium
C24.4.3 - Erzeugung von Blei, Zink und Zinn
C24.4.4 - Erzeugung von Kupfer
C24.4.5 - Sonstige Erzeugung von Nichteisenmetallen
C24.4.6 - Verarbeitung von Kernbrennstoffen
C24.5 - Metallgießereien 
C24.5.1 - Eisengießereien
C24.5.2 - Stahlgießereien
C24.5.3 - Leichtmetallgießereien
C24.5.4 - Sonstige Nichteisenmetallgießereien
C25 - Herstellung von Metallerzeugnissen (ohne Maschinen und Ausrüstungen)
C25.1 - Herstellung von Metallbauteilen 
C25.1.1 - Herstellung von Metallkonstruktionen und Konstruktionsteilen 
C25.1.2 - Herstellung von Türen und Fenstern aus Metall 
C25.2 - Herstellung von Tanks, Sammelbehältern und Behältern aus Metall
C25.2.1 - Herstellung von Heizkörpern und Kesseln für Zentralheizungen
C25.2.9 - Herstellung von sonstigen Tanks, Sammelbehältern und Behältern aus Metall
C25.3 - Herstellung von Dampferzeugern (ohne Warmwasserkessel für Zentralheizungen)
C25.3.0 - Herstellung von Dampferzeugern (ohne Warmwasserkessel für Zentralheizungen)
C25.4 - Herstellung von Waffen und Munition
C25.4.0 - Herstellung von Waffen und Munition
C25.5 - Schmieden, Pressen, Stanzen und Rollformen von Metall; Pulvermetallurgie
C25.5.0 - Schmieden, Pressen, Stanzen und Rollformen von Metall; Pulvermetallurgie
C25.6 - Behandlung und Beschichtung von Metallen; Spanende Bearbeitung
C25.6.1 - Behandlung und Beschichtung von Metallen
C25.6.2 - Spanende Bearbeitung
C25.7 - Herstellung von Schneidwaren, Werkzeugen und Eisenwaren im Allgemeinen
C25.7.1 - Herstellung von Schneidwaren
C25.7.2 - Herstellung von Schlössern und Scharnieren
C25.7.3 - Herstellung von Werkzeugen
C25.9 - Herstellung von sonstigen Metallerzeugnissen
C25.9.1 - Herstellung von Stahlfässern und ähnlichen Behältern
C25.9.2 - Herstellung von Verpackungen aus Leichtmetall
C25.9.3 - Herstellung von Drahtwaren, Ketten und Federn
C25.9.4 - Herstellung von Befestigungselementen und Schraubmaschinenprodukten
C25.9.9 - Herstellung von sonstigen Metallwaren a. g.
C26 - Herstellung von Computer-, elektronischen und optischen Erzeugnissen
C26.1 - Herstellung von elektronischen Bauteilen und Platinen
C26.1.1 - Herstellung von elektronischen Bauteilen
C26.1.2 - Herstellung von bestückten elektronischen Platinen
C26.2 - Herstellung von Computern und Peripheriegeräten
C26.2.0 - Herstellung von Computern und Peripheriegeräten
C26.3 - Herstellung von Kommunikationsgeräten
C26.3.0 - Herstellung von Kommunikationsgeräten 
C26.4 - Herstellung von Unterhaltungselektronik
C26.4.0 - Herstellung von Unterhaltungselektronik
C26.5 - Herstellung von Mess-, Prüf- und Navigationsinstrumenten und -geräten; Uhren und Uhrmacherei
C26.5.1 - Herstellung von Mess-, Kontroll- und Navigationsinstrumenten und -vorrichtungen
C26.5.2 - Herstellung von Uhren und Uhrmacherei
C26.6 - Herstellung von Bestrahlungs-, elektromedizinischen und elektrotherapeutischen Geräten
C26.6.0 - Herstellung von Bestrahlungs-, elektromedizinischen und elektrotherapeutischen Geräten
C26.7 - Herstellung von optischen Instrumenten und fotografischen Geräten
C26.7.0 - Herstellung von optischen Instrumenten und fotografischen Geräten
C26.8 - Herstellung von magnetischen und optischen Datenträgern
C26.8.0 - Herstellung von magnetischen und optischen Datenträgern
C27 - Herstellung von elektrischen Ausrüstungen
C27.1 - Herstellung von Elektromotoren, Generatoren, Transformatoren und Elektrizitätsverteilungs- und -steuergeräten
C27.1.1 - Herstellung von Elektromotoren, Generatoren und Transformatoren
C27.1.2 - Herstellung von Elektrizitätsverteilungs- und -steuergeräten
C27.2 - Herstellung von Batterien und Akkumulatoren
C27.2.0 - Herstellung von Batterien und Akkumulatoren
C27.3 - Herstellung von Verdrahtungen und Verdrahtungsgeräten
C27.3.1 - Herstellung von Glasfaserkabeln
C27.3.2 - Herstellung von sonstigen elektronischen und elektrischen Drähten und Kabeln
C27.3.3 - Herstellung von Installationsgeräten
C27.4 - Herstellung von elektrischen Beleuchtungsgeräten
C27.4.0 - Herstellung von elektrischen Beleuchtungsgeräten
C27.5 - Herstellung von Haushaltsgeräten
C27.5.1 - Herstellung von elektrischen Haushaltsgeräten
C27.5.2 - Herstellung von nichtelektrischen Haushaltsgeräten
C27.9 - Herstellung von sonstigen elektrischen Ausrüstungen
C27.9.0 - Herstellung von sonstigen elektrischen Ausrüstungen
C28 - Herstellung von Maschinen und Ausrüstungen a. g.
C28.1 - Herstellung von nicht wirtschaftszweigspezifischen Maschinen
C28.1.1 - Herstellung von Motoren und Turbinen (ohne Motoren für Luftfahrzeuge, Fahrzeuge und Fahrräder)
C28.1.2 - Herstellung von hydraulischen Ausrüstungen
C28.1.3 - Herstellung von sonstigen Pumpen und Kompressoren
C28.1.4 - Herstellung von sonstigen Armaturen und Ventilen
C28.1.5 - Herstellung von Lagern, Zahnrädern, Getrieben und Antriebselementen
C28.2 - Herstellung von sonstigen nicht wirtschaftszweigspezifischen Maschinen
C28.2.1 - Herstellung von Öfen, Brennern und Brennern
C28.2.2 - Herstellung von Hebezeugen und Fördergeräten
C28.2.3 - Herstellung von Büromaschinen und -geräten (ohne Computer und Peripheriegeräte)
C28.2.4 - Herstellung von motorbetriebenen Handwerkzeugen
C28.2.5 - Herstellung von Kühl- und Lüftungsgeräten, nicht für den Haushalt
C28.2.9 - Herstellung von sonstigen nicht wirtschaftszweigspezifischen Maschinen ang
C28.3 - Herstellung von land- und forstwirtschaftlichen Maschinen
C28.3.0 - Herstellung von land- und forstwirtschaftlichen Maschinen
C28.4 - Herstellung von Maschinen und Werkzeugmaschinen für die Metallumformung
C28.4.1 - Herstellung von Maschinen für die Metallumformung
C28.4.9 - Herstellung von sonstigen Werkzeugmaschinen
C28.9 - Herstellung von sonstigen Maschinen für bestimmte Wirtschaftszweige
C28.9.1 - Herstellung von Maschinen für die Metallurgie
C28.9.2 - Herstellung von Maschinen für Bergbau, Gewinnung von Steinen und Erden und für das Baugewerbe
C28.9.3 - Herstellung von Maschinen für die Nahrungs- und Genussmittelindustrie und die Tabakverarbeitung
C28.9.4 - Herstellung von Maschinen für die Textil-, Bekleidungs- und Lederverarbeitung
C28.9.5 - Herstellung von Maschinen für die Papier- und Kartonherstellung
C28.9.6 - Herstellung von Maschinen zur Verarbeitung von Kunststoffen und Gummi
C28.9.9 - Herstellung von sonstigen Maschinen für bestimmte Wirtschaftszweige ang
C29 - Herstellung von Kraftwagen und Kraftwagenanhängern
C29.1 - Herstellung von Kraftwagen
C29.1.0 - Herstellung von Kraftfahrzeugen
C29.2 - Herstellung von Karosserien für Kraftfahrzeuge; Herstellung von Anhängern und Sattelanhängern
C29.2.0 - Herstellung von Karosserien für Kraftfahrzeuge; Herstellung von Anhängern und Sattelanhängern
C29.3 - Herstellung von Teilen und Zubehör für Kraftfahrzeuge
C29.3.1 - Herstellung von elektrischen und elektronischen Ausrüstungen für Kraftfahrzeuge
C29.3.2 - Herstellung von sonstigen Teilen und Zubehör für Kraftfahrzeuge
C30 - Herstellung von sonstigen Transportmitteln
C30.1 - Schiffs- und Bootsbau
C30.1.1 - Schiffs- und schwimmende Konstruktionen
C30.1.2 - Bau von Sportbooten und Freizeitbooten
C30.2 - Herstellung von Lokomotiven und rollendem Material
C30.2.0 - Herstellung von Lokomotiven und rollendem Material
C30.3 - Herstellung von Luft- und Raumfahrzeugen und entsprechenden Maschinen
C30.3.0 - Herstellung von Luft- und Raumfahrzeugen und entsprechenden Maschinen
C30.4 - Herstellung von militärischen Kampffahrzeugen
C30.4.0 - Herstellung von militärischen Kampffahrzeugen
C30.9 - Herstellung von Transportmitteln, a. g.
C30.9.1 - Herstellung von Motorrädern
C30.9.2 - Herstellung von Fahrrädern und Rollwagen
C30.9.9 - Herstellung von sonstigen Transportmitteln, a. g.
C31 - Herstellung von Möbeln
C31.0 - Herstellung von Möbeln
C31.0.1 - Herstellung von Büro- und Ladenmöbeln
C31.0.2 - Herstellung von Küchenmöbeln
C31.0.3 - Herstellung von Matratzen
C31.0.9 - Herstellung von sonstigen Möbeln
C32 - Herstellung von sonstigen Erzeugnissen
C32.1 - Herstellung von Schmuck, Juwelen und ähnlichen Erzeugnissen
C32.1.1 - Prägen von Münzen 
C32.1.2 - Herstellung von Schmuck und ähnlichen Erzeugnissen
C32.1.3 - Herstellung von Modeschmuck und ähnlichen Erzeugnissen
C32.2 - Herstellung von Musikinstrumenten
C32.2.0 - Herstellung von Musikinstrumenten 
C32.3 - Herstellung von Sportartikeln
C32.3.0 - Herstellung von Sportartikeln
C32.4 - Herstellung von Spielen und Spielzeug
C32.4.0 - Herstellung von Spielen und Spielzeug
C32.5 - Herstellung von medizinischen und zahnmedizinischen Instrumenten und Materialien
C32.5.0 - Herstellung von medizinischen und zahnmedizinischen Instrumenten und Materialien
C32.9 - Herstellung von Waren ohne besondere Kenntnisse
C32.9.1 - Herstellung von Besen und Bürsten
C32.9.9 - Herstellung von sonstigen Erzeugnissen ohne besondere Kenntnisse
C33 - Reparatur und Installation von Maschinen und Geräten 
C33.1 - Reparatur von
C33.1.1 - Reparatur von Metallerzeugnissen
C33.1.2 - Reparatur von Maschinen
C33.1.3 - Reparatur von elektronischen und optischen Geräten
C33.1.4 - Reparatur von elektrischen Geräten
C33.1.5 - Reparatur und Wartung von Schiffen und Booten
C33.1.6 - Reparatur und Wartung von Luft- und Raumfahrzeugen
C33.1.7 - Reparatur und Wartung von sonstigen Transportgeräten
C33.1.9 - Reparatur von sonstigen Geräten
C33.2 - Installation von industriellen Maschinen und Geräten
C33.2.0 - Installation von industriellen Maschinen und Geräten
D - Strom-, Gas-, Dampf- und Klimaanlagenversorgung
D35 - Strom-, Gas-, Dampf- und Klimaanlagenversorgung 
D35.1 - Stromerzeugung, -übertragung und -verteilung 
D35.1.1 - Stromerzeugung
D35.1.2 - Stromübertragung
D35.1.3 - Stromverteilung
D35.1.4 - Stromhandel
D35.2 - Gasherstellung; Verteilung gasförmiger Brennstoffe über Leitungen
D35.2.1 - Gasherstellung
D35.2.2 - Verteilung gasförmiger Brennstoffe über Leitungen
D35.2.3 - Gashandel über Leitungen
D35.3 - Dampf- und Klimaanlagenversorgung
D35.3.0 - Dampf- und Klimaanlagenversorgung
E - Wasserversorgung; Kanalisation; Abfallbewirtschaftung und -beseitigung
E36 - Wassersammlung, -aufbereitung und -versorgung
E36.0 - Wassersammlung, -aufbereitung und -versorgung
E36.0.0 - Wassersammlung, -aufbereitung und -versorgung
E37 - Kanalisation
E37.0 - Kanalisation
E37.0.0 - Kanalisation
E38 - Abfallsammlung, -aufbereitung und -entsorgung; Materialrückgewinnung
E38.1 - Abfallsammlung
E38.1.1 - Sammlung nicht gefährlicher Abfälle
E38.1.2 - Sammlung gefährlicher Abfälle
E38.2 - Abfallbehandlung und -entsorgung
E38.2.1 - Behandlung und Entsorgung nicht gefährlicher Abfälle
E38.2.2 - Behandlung und Entsorgung gefährlicher Abfälle
E38.3 - Materialrückgewinnung
E38.3.1 - Demontage von Wracks
E38.3.2 - Rückgewinnung sortierter Materialien
E39 - Sanierungstätigkeiten und sonstige Abfallbewirtschaftung
E39.0 - Sanierungstätigkeiten und sonstige Abfallbewirtschaftung
E39.0.0 - Sanierungstätigkeiten und sonstige Abfallbewirtschaftung
F - Baugewerbe
F41 - Bau von Gebäuden
F41.1 - Entwicklung von Bauprojekten
F41.1.0 - Entwicklung von Bauprojekten
F41.2 - Bau von Wohn- und Nichtwohngebäuden
F41.2.0 - Bau von Wohn- und Nichtwohngebäuden
F42 - Tiefbau
F42.1 - Bau von Straßen und Eisenbahnen
F42.1.1 - Bau von Straßen und Autobahnen
F42.1.2 - Bau von Eisenbahnen und U-Bahnen
F42.1.3 - Bau von Brücken und Tunneln
F42.2 - Bau von Versorgungsprojekten
F42.2.1 - Rohrleitungsbau für Flüssigkeiten
F42.2.2 - Rohrleitungsbau für Elektrizität und Telekommunikation
F42.9 - Sonstiger Tiefbau
F42.9.1 - Wasserbau
F42.9.9 - Sonstiger Tiefbau ang
F43 - Vorbereitende Bauarbeiten
F43.1 - Abbrucharbeiten und vorbereitende Baustellenarbeiten
F43.1.1 - Abbrucharbeiten
F43.1.2 - Vorbereitende Baustellenarbeiten
F43.1.3 - Probebohrungen und -bohrungen
F43.2 - Elektro-, Klempner- und sonstige Bauinstallationstätigkeiten
F43.2.1 - Elektroinstallation
F43.2.2 - Klempner-, Heizungs- sowie Klimaanlageninstallation
F43.2.9 - Sonstige Bauinstallation
F43.3 - Sonstiger Bauausbau
F43.3.1 - Verputzarbeiten
F43.3.2 - Bautischlerei und -bau
F43.3.3 - Bodenbelags- und Tapezierarbeiten
F43.3.4 - Maler- und Glaserarbeiten
F43.3.9 - Sonstiger Bauausbau
F43.9 - Sonstige spezialisierte Bautätigkeiten
F43.9.1 - Dachdeckerarbeiten
F43.9.9 - Sonstige spezialisierte Bautätigkeiten
G - Groß- und Einzelhandel; Reparatur von Kraftfahrzeugen und Motorrädern
G45 - Groß- und Einzelhandel und Reparatur von Kraftfahrzeugen und Motorrädern
G45.1 - Handel mit Kraftfahrzeugen
G45.1.1 - Handel mit Personenkraftwagen und leichten Kraftfahrzeugen
G45.1.9 - Handel mit sonstigen Kraftfahrzeugen
G45.2 - Instandhaltung und Reparatur von Kraftfahrzeugen
G45.2.0 - Instandhaltung und Reparatur von Kraftfahrzeugen
G45.3 - Handel mit Kraftfahrzeugteilen und Zubehör
G45.3.1 - Großhandel mit Kraftfahrzeugteilen und Zubehör
G45.3.2 - Einzelhandel mit Kraftfahrzeugteilen und Zubehör
G45.4 - Verkauf, Instandhaltung und Reparatur von Motorrädern und dazugehörigen Teilen und Zubehör
G45.4.0 - Verkauf, Instandhaltung und Reparatur von Motorrädern und dazugehörigen Teilen und Zubehör
G46 - Großhandel (ohne Handel mit Kraftfahrzeugen und Motorrädern)
G46.1 - Großhandel auf Honorar- oder Vertragsbasis
G46.1.1 - Handelsvermittlung von landwirtschaftlichen Rohstoffen, lebenden Tieren, textilen Rohstoffen und Halbfabrikaten
G46.1.2 - Handelsvermittlung von Brennstoffe, Erze, Metalle und Industriechemikalien
G46.1.3 - Handelsvermittlung von Holz und Baustoffen
G46.1.4 - Handelsvermittlung von Maschinen, Industrieanlagen, Schiffen und Flugzeugen
G46.1.5 - Verkaufsmakler für Möbel, Haushaltswaren, Eisen- und Metallwaren
G46.1.6 - Verkaufsmakler für Textilien, Bekleidung, Pelze, Schuhe und Lederwaren
G46.1.7 - Verkaufsmakler für Nahrungsmittel, Getränke und Tabak
G46.1.8 - Verkaufsmakler für sonstige bestimmte Erzeugnisse
G46.1.9 - Verkaufsmakler für verschiedene Waren
G46.2 - Großhandel mit landwirtschaftlichen Rohstoffen und lebenden Tieren
G46.2.1 - Großhandel mit Getreide, Rohtabak, Saatgut und Futtermitteln
G46.2.2 - Großhandel mit Blumen und Pflanzen 
G46.2.3 - Großhandel mit lebenden Tieren 
G46.2.4 - Großhandel mit Häuten, Fellen und Leder
G46.3 - Großhandel mit Nahrungsmitteln, Getränken und Tabak
G46.3.1 - Großhandel mit Obst und Gemüse
G46.3.2 - Großhandel mit Fleisch und Fleischwaren
G46.3.3 - Großhandel mit Milchprodukten , Eiern und Speiseölen und -fetten
G46.3.4 - Getränkegroßhandel
G46.3.5 - Tabakgroßhandel
G46.3.6 - Zuckergroßhandel und Schokolade und Zuckerwaren
G46.3.7 - Kaffeegroßhandel, Teegroßhandel, Kakaogroßhandel und Gewürzen
G46.3.8 - Sonstiger Nahrungsmittelgroßhandel 
G46.3.9 - Großhandel mit Nahrungsmitteln, Getränken und Tabakwaren ohne ausgeprägten Schwerpunkt
G46.4 - Großhandel mit Gebrauchs- und Verbrauchsgütern
G46.4.1 - Textiliengroßhandel
G46.4.2 - Bekleidungsgroßhandel und Schuhgroßhandel
G46.4.3 - Elektrische Haushaltsgeräte
G46.4.4 - Großhandel mit Porzellan, Glaswaren und Reinigungsmitteln
G46.4.5 - Parfümerien und Kosmetikartikel
G46.4.6 - Pharmagroßhandel
G46.4.7 - Möbelgroßhandel, Teppichgroßhandel und Beleuchtungskörper
G46.4.8 - Uhrengroßhandel und Schmuck
G46.4.9 - Großhandel mit sonstigen Gebrauchs- und Verbrauchsgütern
G46.5 - Großhandel mit Geräten der Informations- und Kommunikationstechnik
G46.5.1 - Großhandel mit Computern, Computerperipheriegeräten und Software
G46.5.2 - Großhandel mit elektronischen Geräten und Teilen der Telekommunikationstechnik
G46.6 - Großhandel mit sonstigen Maschinen, Geräten und Zubehör
G46.6.1 - Großhandel mit landwirtschaftlichen Maschinen, Geräten und Zubehör
G46.6.2 - Großhandel mit Werkzeugmaschinen
G46.6.3 - Großhandel mit Maschinen für den Bergbau, das Hoch- und Tiefbau
G46.6.4 - Großhandel mit Maschinen für die Textilindustrie sowie mit Näh- und Strickmaschinen
G46.6.5 - Großhandel mit Büromöbeln
G46.6.6 - Großhandel mit sonstigen Büromaschinen und -geräten
G46.6.9 - Großhandel mit sonstigen Maschinen und Geräten
G46.7 - Sonstiger spezialisierter Großhandel
G46.7.1 - Großhandel mit festen, flüssigen und gasförmigen Brennstoffen und verwandten Erzeugnissen
G46.7.2 - Großhandel mit Metallen und Erzen
G46.7.3 - Großhandel mit Holz, Baustoffen und Sanitärkeramik
G46.7.4 - Großhandel mit Eisen- und Metallwaren, Installations- und Heizungsanlagen und -bedarf
G46.7.5 - Großhandel mit chemischen Erzeugnissen
G46.7.6 - Großhandel mit sonstigen Halberzeugnissen 
G46.7.7 - Großhandel mit Altmaterialien und Schrott
G46.9 - Großhandel ohne spezialisierten Schwerpunkt
G46.9.0 - Großhandel ohne spezialisierten Schwerpunkt
G47 - Einzelhandel (ohne Handel mit Kraftfahrzeugen und Krafträdern)
G47.1 - Einzelhandel mit nicht spezialisierten Verkaufsräumen
G47.1.1 - Einzelhandel mit nicht spezialisierten Verkaufsräumen, mit Hauptschwerpunkt Nahrungsmittel, Getränke und Tabakwaren
G47.1.9 - Sonstiger Einzelhandel mit nicht spezialisierter Einzelhandel mit Nahrungsmitteln, Getränken und Tabakwaren 
G47.2 - Einzelhandel mit Nahrungsmitteln, Getränken und Tabakwaren in Fachgeschäften
G47.2.1 - Einzelhandel mit Obst und Gemüse in Fachgeschäften
G47.2.2 - Einzelhandel mit Fleisch und Fleischwaren in Fachgeschäften
G47.2.3 - Einzelhandel mit Fisch, Krebstieren und Weichtieren in Fachgeschäften
G47.2.4 - Einzelhandel mit Brot, Kuchen, Mehlwaren und Zuckerwaren in Fachgeschäften
G47.2.5 - Einzelhandel mit Getränken in Fachgeschäften
G47.2.6 - Einzelhandel mit Tabakwaren in Fachgeschäften
G47.2.9 - Sonstiger Einzelhandel mit Nahrungsmitteln in Fachgeschäften
G47.3 - Einzelhandel mit Kraftstoffen in Fachgeschäften 
G47.3.0 - Einzelhandel mit Kraftstoffen in Fachgeschäften
G47.4 - Einzelhandel mit Informations- und Kommunikationsgeräten in Fachgeschäften
G47.4.1 - Einzelhandel mit Computern, Peripheriegeräten und Software in Fachgeschäften
G47.4.2 - Einzelhandel mit Telekommunikationsgeräten (in Fachgeschäften)
G47.4.3 - Einzelhandel mit Audio- und Videogeräten (in Fachgeschäften)
G47.5 - Einzelhandel mit sonstigen Haushaltsgeräten (in Fachgeschäften)
G47.5.1 - Einzelhandel mit Textilien (in Fachgeschäften)
G47.5.2 - Einzelhandel mit Eisenwaren, Farben und Glas (in Fachgeschäften)
G47.5.3 - Einzelhandel mit Teppichen, Läufern, Wand- und Bodenbelägen (in Fachgeschäften)
G47.5.4 - Einzelhandel mit elektrischen Haushaltsgeräten (in Fachgeschäften)
G47.5.9 - Einzelhandel mit Möbeln, Beleuchtungskörpern und sonstigen Haushaltsartikeln (in Fachgeschäften)
G47.6 - Einzelhandel mit Kultur- und Freizeitartikeln (in Fachgeschäften)
G47.6.1 - Einzelhandel mit Büchern (in Fachgeschäften)
G47.6.2 - Einzelhandel mit Zeitungen und Schreibwaren (in Fachgeschäften)
G47.6.3 - Einzelhandel mit Musik- und Videoaufnahmen (in Fachgeschäften)
G47.6.4 - Einzelhandel mit Sportgeräten (in Fachgeschäften)
G47.6.5 - Einzelhandel mit Spielen und Spielsachen (in Fachgeschäften)
G47.7 - Einzelhandel mit sonstigen Gütern (in Fachgeschäften)
G47.7.1 - Einzelhandel mit Bekleidung (in Fachgeschäften)
G47.7.2 - Einzelhandel mit Schuhen und Lederwaren (in Fachgeschäften)
G47.7.3 - Apotheken (in Fachgeschäften)
G47.7.4 - Einzelhandel mit medizinischen und orthopädischen Artikeln (in Fachgeschäften)
G47.7.5 - Einzelhandel mit Kosmetik- und Toilettenartikeln (in Fachgeschäften)
G47.7.6 - Einzelhandel mit Blumen, Pflanzen, Saatgut, Düngemitteln, Heimtieren Lebensmittel in Fachgeschäften
G47.7.7 - Einzelhandel mit Uhren und Schmuck in Fachgeschäften
G47.7.8 - Sonstiger Einzelhandel mit Neuwaren in Fachgeschäften
G47.7.9 - Einzelhandel mit Gebrauchtwaren in Geschäften
G47.8 - Einzelhandel an Verkaufsständen und auf Märkten
G47.8.1 - Einzelhandel mit Nahrungsmitteln, Getränken und Tabakwaren an Verkaufsständen und auf Märkten
G47.8.2 - Einzelhandel mit Textilien, Bekleidung und Schuhen an Verkaufsständen und auf Märkten
G47.8.9 - Einzelhandel mit sonstigen Gütern an Verkaufsständen und auf Märkten
G47.9 - Einzelhandel, nicht in Geschäften, an Verkaufsständen und auf Märkten
G47.9.1 - Versandhandel und Internet
G47.9.9 - Sonstiger Einzelhandel, nicht in Geschäften, an Verkaufsständen und auf Märkten
H - Transport und Lagerung
H49 - Landtransport und Transport in Rohrfernleitungen
H49.1 - Personenverkehr auf der Schiene, Interurban
H49.1.0 - Personenverkehr auf der Schiene, Interurban
H49.2 - Güterverkehr auf der Schiene
H49.2.0 - Güterbeförderung auf der Schiene
H49.3 - Sonstige Personenbeförderung zu Lande
H49.3.1 - Stadt- und Vorort-Personenbeförderung zu Lande
H49.3.2 - Taxibetrieb
H49.3.9 - Sonstige Personenbeförderung zu Lande, ang
H49.4 - Güterbeförderung auf der Straße und Umzugsdienstleistungen
H49.4.1 - Güterbeförderung auf der Straße
H49.4.2 - Umzugsdienstleistungen
H49.5 - Transport durch Rohrleitungen 
H49.5.0 - Transport durch Rohrleitungen 
H50 - Transport auf der Wasserstraße
H50.1 - Personenbeförderung zu Wasser und an der Küste 
H50.1.0 - Personenbeförderung zu Wasser und an der Küste 
H50.2 - Güterbeförderung zu Wasser und an der Küste
H50.2.0 - Güterbeförderung auf See und in Küstennähe 
H50.3 - Personenbeförderung auf Binnenwasserstraßen 
H50.3.0 - Personenbeförderung auf Binnenwasserstraßen 
H50.4 - Güterbeförderung auf Binnenwasserstraßen 
H50.4.0 - Güterbeförderung auf Binnenwasserstraßen
H51 - Luftverkehr
H51.1 - Personenbeförderung auf Luftstraßen
H51.1.0 - Personenbeförderung auf Luftstraßen
H51.2 - Frachtbeförderung auf Luftstraßen und Raumtransport
H51.2.1 - Frachtbeförderung auf Luftstraßen
H51.2.2 - Raumtransport
H52 - Lagerei und unterstützende Tätigkeiten für den Verkehr
H52.1 - Lagerei und Aufbewahrung
H52.1.0 - Lagerei und Aufbewahrung
H52.2 - Unterstützende Tätigkeiten für den Verkehr
H52.2.1 - Erbringung von sonstigen Dienstleistungen für den Landtransport
H52.2.2 - Erbringung von sonstigen Dienstleistungen für den Wassertransport
H52.2.3 - Erbringung von sonstigen Dienstleistungen für den Luftverkehr
H52.2.4 - Frachtumschlag
H52.2.9 - Sonstige unterstützende Tätigkeiten für den Verkehr
H53 - Post-, Kurier- und Expressdienste
H53.1 - Postdienstleistungen mit Universaldienstverpflichtung
H53.1.0 - Postdienstleistungen mit Universaldienstverpflichtung
H53.2 - Sonstige Post- und Kurierdienste
H53.2.0 - Sonstige Post- und Kurierdienste
I - Beherbergung und Gastronomie
I55 - Beherbergung
I55.1 - Hotels und ähnliche Beherbergungsbetriebe
I55.1.0 - Hotels und ähnliche Beherbergungsbetriebe
I55.2 - Ferienunterkünfte und sonstige Beherbergungsbetriebe
I55.2.0 - Ferienunterkünfte und sonstige Beherbergungsbetriebe
I55.3 - Campingplätze, Wohnmobilstellplätze und Wohnwagenparks
I55.3.0 - Campingplätze, Wohnmobilstellplätze und Wohnwagenparks
I55.9 - Sonstige Beherbergungsbetriebe
I55.9.0 - Sonstige Beherbergungsbetriebe
I56 - Gastronomie
I56.1 - Restaurants, Imbissbuden und Ausschank von Speisen
I56.1.0 - Restaurants, Imbissbuden und Ausschank von Speisen
I56.2 - Event-Catering und sonstige Beherbergungsbetriebe
I56.2.1 - Event-Catering
I56.2.9 - Sonstige Beherbergungsbetriebe
I56.3 - Ausschank von Getränken
I56.3.0 - Ausschank von Getränken
J - Information und Kommunikation
J58 - Verlagswesen
J58.1 - Verlegen von Büchern, Zeitschriften und sonstigem Verlagswesen
J58.1.1 - Verlegen von Büchern
J58.1.2 - Verlegen von Verzeichnissen und Mailinglisten
J58.1.3 - Verlegen von Zeitungen
J58.1.4 - Verlegen von Zeitschriften und Periodika
J58.1.9 - Sonstiges Verlagswesen
J58.2 - Verlegen von Software
J58.2.1 - Verlegen von Computerspielen
J58.2.9 - Sonstiges Softwareverlagswesen
J59 - Produktion von Film-, Video- und Fernsehprogrammen, Tonaufzeichnungen und Musikverlage
J59.1 - Tätigkeiten im Bereich Film-, Video- und Fernsehprogramme 
J59.1.1 - Produktion von Film-, Video- und Fernsehprogrammen
J59.1.2 - Nachbearbeitung von Film-, Video- und Fernsehprogrammen
J59.1.3 - Vertrieb von Film-, Video- und Fernsehprogrammen
J59.1.4 - Vorführung von Filmen
J59.2 - Tonaufzeichnungen und Musikverlage 
J59.2.0 - Tonaufzeichnungen und Musikverlage
J60 - Sende- und Rundfunktätigkeiten
J60.1 - Rundfunk 
J60.1.0 - Rundfunk
J60.2 - Fernsehsendungen und -rundfunktätigkeiten
J60.2.0 - Fernsehsendungen und -rundfunktätigkeiten
J61 - Telekommunikation
J61.1 - Leitungsgebundene Telekommunikation
J61.1.0 - Leitungsgebundene Telekommunikation
J61.2 - Drahtlose Telekommunikation
J61.2.0 - Drahtlose Telekommunikation
J61.3 - Satellitentelekommunikation
J61.3.0 - Satellitentelekommunikation
J61.9 - Sonstige Telekommunikationstätigkeiten
J61.9.0 - Sonstige Telekommunikationstätigkeiten
J62 - Erbringung von Dienstleistungen der Computerprogrammierung und -beratung sowie damit verbundene Tätigkeiten
J62.0 - Erbringung von Dienstleistungen der Computerprogrammierung
J62.0.2 - EDV-Beratung
J62.0.3 - Verwaltung von EDV-Anlagen
J62.0.9 - Sonstige Tätigkeiten der Informationstechnologie und Computerdienste
J63 - Erbringung von Informationsdienstleistungen
J63.1 - Datenverarbeitung, Hosting und damit verbundene Tätigkeiten; Webportale
J63.1.1 - Datenverarbeitung, Hosting und damit verbundene Tätigkeiten
J63.1.2 - Webportale
J63.9 - Erbringung sonstiger Informationsdienstleistungen
J63.9.1 - Nachrichtenagenturen
J63.9.9 - Erbringung sonstiger Informationsdienstleistungen
K - Erbringung von Finanz- und Versicherungsdienstleistungen
K64 - Erbringung von Finanzdienstleistungen (ohne Versicherungs- und Pensionskassen)
K64.1 - Kreditinstitute und sonstige Kreditinstitute
K64.1.1 - Zentralbanken
K64.1.9 - Sonstige Kreditinstitute und sonstige Kreditinstitute
K64.2 - Holdinggesellschaften
K64.2.0 - Holdinggesellschaften
K64.3 - Treuhandgesellschaften, Fonds und ähnliche Finanzinstitute
K64.3.0 - Treuhandgesellschaften, Fonds und ähnliche Finanzinstitute
K64.9 - Erbringung sonstiger Finanzdienstleistungen (ohne Versicherungs- und Pensionskassen)
K64.9.1 - Finanzierungsleasing
K64.9.2 - Sonstige Kreditgewährung
K64.9.9 - Erbringung sonstiger Finanzdienstleistungen (ohne Versicherungs- und Pensionskassen)
K65 - Versicherungen, Rückversicherungen und Pensionskassen (ohne Sozialversicherungswesen)
K65.1 - Versicherungen
K65.1.1 - Lebensversicherungen
K65.1.2 - Nichtlebensversicherungen
K65.2 - Rückversicherungen
K65.2.0 - Rückversicherungen
K65.3 - Pensionskassen
K65.3.0 - Pensionskassen
K66 - Mit Finanzdienstleistungen und Versicherungsdienstleistungen verbundene Tätigkeiten
K66.1 - Mit Finanzdienstleistungen verbundene Tätigkeiten (ohne Versicherungs- und Pensionskassen)
K66.1.1 - Verwaltung der Finanzmärkte
K66.1.2 - Vermittlung von Wertpapier- und Warenkontrakten
K66.1.9 - Sonstige mit Finanzdienstleistungen verbundene Tätigkeiten (außer Versicherungs- und Pensionskassen)
K66.2 - Mit Versicherungs- und Pensionskassen verbundene Tätigkeiten
K66.2.1 - Risiko- und Schadensbewertung
K66.2.2 - Tätigkeit von Versicherungsvertretern und -maklern
K66.2.9 - Sonstige mit Versicherungs- und Pensionskassen verbundene Tätigkeiten
K66.3 - Fondsverwaltung
K66.3.0 - Fondsverwaltung
L - Immobiliendienstleistungen
L68 - Immobiliendienstleistungen
L68.1 - Kauf und Verkauf von eigenen Immobilien
L68.1.0 - Kauf und Verkauf von eigenen Immobilien
L68.2 - Vermietung und Verwaltung von eigenen oder gepachteten Immobilien
L68.2.0 - Vermietung und Verwaltung von eigenen oder gepachteten Immobilien
L68.3 - Immobiliendienstleistungen gegen Entgelt oder auf Auftragsbasis
L68.3.1 - Immobilienvermittlung
L68.3.2 - Immobilienverwaltung gegen Entgelt oder auf Auftragsbasis
M - Freiberufliche, wissenschaftliche und technische Tätigkeiten
M69 - Rechtsdienstleistungen, Buchführung und Wirtschaftsprüfung; Steuerberatung
M69.1 - Rechtsdienstleistungen
M69.1.0 - Rechtsdienstleistungen
M69.2 - Wirtschaftsprüfung und Buchführung; Steuerberatung
M69.2.0 - Wirtschaftsprüfung und Buchführung; Steuerberatung
M70 - Tätigkeiten von Unternehmen und Hauptverwaltungen; Managementberatung
M70.1 - Tätigkeiten von Unternehmen und Hauptverwaltungen
M70.1.0 - Tätigkeiten von Unternehmen und Hauptverwaltungen
M70.2 - Public-Relations- und Kommunikationsdienstleistungen
M70.2.2 - Unternehmensberatung und sonstige Managementberatung
M71 - Architektur- und Ingenieurbüros; technische Prüfungen und Analysen
M71.1 - Architektur- und Ingenieurtätigkeiten und damit verbundene technische Beratung
M71.1.1 - Architekturtätigkeiten
M71.1.2 - Ingenieurtätigkeiten und damit verbundene technische Beratung
M71.2 - Technische Prüfungen und Analysen
M71.2.0 - Technische Prüfungen und Analysen
M72 - Wissenschaftliche Forschung und Entwicklung
M72.1 - Forschung und experimentelle Entwicklung in Naturwissenschaften und Ingenieurwissenschaften
M72.1.1 - Forschung und experimentelle Entwicklung in Biotechnologie
M72.1.9 - Sonstige Forschung und experimentelle Entwicklung in Naturwissenschaften und Ingenieurwissenschaften
M72.2 - Forschung und experimentelle Entwicklung in Sozialwissenschaften und Geisteswissenschaften
M72.2.0 - Forschung und experimentelle Entwicklung in Sozialwissenschaften und Geisteswissenschaften
M73 - Werbung und Marktforschung 
M73.1 - Werbung
M73.1.1 - Werbeagenturen
M73.1.2 - Medienvertretung
M73.2 - Markt- und Meinungsforschung
M73.2.0 - Markt- und Meinungsforschung 
M74 - Sonstige freiberufliche, wissenschaftliche und technische Tätigkeiten Designtätigkeiten
M74.1.0 - Designtätigkeiten
M74.2 - Fotografische Tätigkeiten
M74.2.0 - Fotografische Tätigkeiten
M74.3 - Übersetzer- und Dolmetschertätigkeiten
M74.3.0 - Übersetzer- und Dolmetschertätigkeiten
M74.9 - Sonstige freiberufliche, wissenschaftliche und technische Tätigkeiten ang
M74.9.0 - Sonstige freiberufliche, wissenschaftliche und technische Tätigkeiten ang
M75 - Veterinärwesen
M75.0 - Veterinärwesen
M75.0.0 - Veterinärwesen
N - Erbringung von sonstigen Verwaltungsdienstleistungen
N77 - Vermietung und Leasing 
N77.1 - Vermietung und Leasing von Kraftfahrzeugen
N77.1.1 - Vermietung und Leasing von Personenkraftwagen und leichten Kraftfahrzeugen
N77.1.2 - Vermietung und Leasing von Lastkraftwagen
N77.2 - Vermietung und Leasing von persönlichen Gegenständen und Haushaltsgegenständen
N77.2.1 - Vermietung und Leasing von Freizeit- und Sportartikeln
N77.2.2 - Vermietung von Videobändern und -disks
N77.2.9 - Miete und Leasing von sonstigen persönlichen und Haushaltsgegenständen
N77.3 - Miete und Leasing von sonstigen Maschinen, Geräten und materiellen Gütern
N77.3.1 - Vermietung und Leasing von landwirtschaftlichen Maschinen und Geräten
N77.3.2 - Vermietung und Leasing von Maschinen und Geräten für das Hoch- und Tiefbau
N77.3.3 - Vermietung und Leasing von Büromaschinen und -geräten (einschließlich Computern)
N77.3.4 - Vermietung und Leasing von Wassertransportausrüstung
N77.3.5 - Vermietung und Leasing von Lufttransportausrüstung
N77.3.9 - Vermietung und Leasing von sonstigen Maschinen, Ausrüstungen und materiellen Gütern ang
N77.4 - Leasing von geistigem Eigentum und ähnlichen Produkten, ausgenommen urheberrechtlich geschützte Werke
N77.4.0 - Leasing von geistigem Eigentum und ähnlichen Produkten, ausgenommen urheberrechtlich geschützte Werke
N78 - Vermittlung von Arbeitskräften
N78.1 - Tätigkeiten von Arbeitsvermittlungen
N78.1.0 - Tätigkeiten von Arbeitsvermittlungen
N78.2 - Überlassung von Arbeitskräften
N78.2.0 - Überlassung von Arbeitskräften
N78.3 - Sonstige Überlassung von Arbeitskräften
N78.3.0 - Sonstige Überlassung von Arbeitskräften
N79 - Reisebüros, Reiseveranstalter und sonstige Reservierungsdienste und damit verbundene Tätigkeiten
N79.1 - Reisebüros und Reiseveranstalter
N79.1.1 - Reisebüros
N79.1.2 - Reiseveranstalter
N79.9 - Sonstige Reservierungsdienste und damit verbundene Tätigkeiten
N79.9.0 - Sonstige Reservierungsdienste und damit verbundene Tätigkeiten
N80 - Wach- und Sicherheitsdienste und Ermittlungstätigkeiten
N80.1 - Private Wach- und Sicherheitsdienste
N80.1.0 - Private Wach- und Sicherheitsdienste
N80.2 - Dienste für Sicherheitssysteme
N80.2.0 - Dienste für Sicherheitssysteme
N80.3 - Ermittlungstätigkeiten
N80.3.0 - Ermittlungstätigkeiten
N81 - Gebäude- und Landschaftsbaudienstleistungen
N81.1 - Kombinierte Einrichtungenbetreuung
N81.1.0 - Kombinierte Einrichtungenbetreuung
N81.2 - Reinigungstätigkeiten
N81.2.1 - Allgemeine Gebäudereinigung
N81.2.2 - Sonstige Gebäude- und Industriereinigung
N81.2.9 - Sonstige Reinigungstätigkeiten
N81.3 - Landschaftsbaudienstleistungen
N81.3.0 - Landschaftsbaudienstleistungen
N82 - Bürodienstleistungen und sonstige unterstützende Tätigkeiten
N82.1 - Allgemeine Bürodienstleistungen
N82.1.1 - Allgemeine Bürodienstleistungen
N82.1.9 - Fotokopieren, Dokumentenvorbereitung und sonstige spezialisierte Bürodienstleistungen
N82.2 - Call-Center
N82.2.0 - Call-Center
N82.3 - Messe- und Kongressveranstalter
N82.3.0 - Messe- und Kongressveranstalter
N82.9 - Erbringung von betriebswirtschaftlichen und geschäftlichen Dienstleistungen, a. g.
N82.9.1 - Inkassobüros und Kreditauskunfteien
N82.9.2 - Verpackungsdienstleistungen
N82.9.9 - Erbringung von sonstigen betriebswirtschaftlichen und geschäftlichen Dienstleistungen, a. g.
O - Öffentliche Verwaltung, Verteidigung; soziale Sicherheit
O84 - Öffentliche Verwaltung, Verteidigung; obligatorische soziale Sicherheit
O84.1 - Staatsverwaltung und Wirtschafts- und Sozialpolitik der Gemeinschaft
O84.1.1 - Allgemeine öffentliche Verwaltungstätigkeiten
O84.1.2 - Regulierung der Tätigkeiten zur Bereitstellung von Gesundheitsfürsorge, Bildung, kulturellen Dienstleistungen und anderen sozialen Dienstleistungen, ausgenommen soziale Sicherheit
O84.1.3 - Regulierung von und Beitrag zu effizienterem Betrieb von Unternehmen
O84.2 - Bereitstellung von Dienstleistungen für die Gemeinschaft als Ganzes
O84.2.1 - Auswärtige Angelegenheiten
O84.2.2 - Verteidigungstätigkeiten 
O84.2.3 - Justiz und Rechtsprechung
O84.2.4 - Öffentliche Ordnung und Sicherheit
O84.2.5 - Feuerwehr
O84.3 - obligatorische soziale Sicherheit 
O84.3.0 - obligatorische soziale Sicherheit
P - Bildung
P85 - Bildung
P85.1 - Vorschulische Bildung
P85.1.0 - Vorschulische Bildung
P85.2 - Primarschulbildung
P85.2.0 - Primarschulbildung
P85.3 - Sekundarschulbildung
P85.3.1 - Allgemeinbildender Sekundarunterricht
P85.3.2 - Technischer und beruflicher Sekundarunterricht
P85.4 - Hochschulbildung
P85.4.1 - Postsekundärer, nicht tertiärer Unterricht
P85.4.2 - Tertiärer Unterricht
P85.5 - Sonstiger Unterricht
P85.5.1 - Sport- und Freizeitunterricht
P85.5.2 - Kulturunterricht
P85.5.3 - Fahrschulen
P85.5.9 - Sonstiger Unterricht, a. g.
P85.6 - Unterrichtsunterstützende Tätigkeiten
P85.6.0 - Unterrichtsunterstützende Tätigkeiten
Q - Gesundheitswesen und Sozialwesen
Q86 - Gesundheitswesen
Q86.1 - Krankenhäuser
Q86.1.0 - Krankenhäuser
Q86.2 - Arzt- und Zahnarztpraxen
Q86.2.1 - Allgemeinmedizinische Arztpraxen
Q86.2.2 - Facharztpraxen
Q86.2.3 - Zahnarztpraxen
Q86.9 - Sonstige Gesundheitswesen
Q86.9.0 - Sonstige Tätigkeiten des Gesundheitswesens
Q87 - Heimpflege
Q87.1 - Krankenpflege in Heimen
Q87.1.0 - Krankenpflege in Heimen
Q87.2 - Heime für Geistige Behinderung, psychische Erkrankungen und Drogenmissbrauch
Q87.2.0 - Heime für Geistige Behinderung, psychische Erkrankungen und Drogenmissbrauch
Q87.3 - Heime für Alte und Behinderte
Q87.3.0 - Heime für Alte und Behinderte
Q87.9 - Sonstige Heimpflege
Q87.9.0 - Sonstige Heimpflege
Q88 - Sozialwesen ohne Unterbringung
Q88.1 - Sozialwesen ohne Unterbringung für Alte und Behinderte
Q88.1.0 - Sozialwesen ohne Unterbringung für Alte und Behinderte
Q88.9 - Sonstiges Sozialwesen ohne Unterbringung
Q88.9.1 - Kindertagesstätten
Q88.9.9 - Sonstiges Sozialwesen ohne Unterbringung, ang
R - Kunst, Unterhaltung und Erholung
R90 - Kreative, künstlerische und unterhaltende Tätigkeiten
R90.0 - Kreative, künstlerische und unterhaltende Tätigkeiten
R90.0.1 - Darstellende Künste
R90.0.2 - Unterstützende Tätigkeiten für darstellende Künste
R90.0.3 - Künstlerisches Schaffen
R90.0.4 - Betrieb von Kunsteinrichtungen
R91 - Bibliotheken, Archive, Museen und sonstige kulturelle Tätigkeiten
R91.0 - Bibliotheken, Archive, Museen und sonstige kulturelle Tätigkeiten
R91.0.1 - Bibliotheks- und Archivtätigkeiten
R91.0.2 - Museumstätigkeiten
R91.0.3 - Betrieb von historischen Stätten und Gebäuden und ähnlichen Besucherattraktionen
R91.0.4 - Botanische und zoologische Gärten und Naturschutzgebiete
R92 - Glücks- und Wettaktivitäten
R92.0 - Glücks- und Wettaktivitäten
R92.0.0 - Glücks- und Wettaktivitäten
R93 - Sportaktivitäten und Aktivitäten der Unterhaltung und Erholung
R93.1 - Sportaktivitäten
R93.1.1 - Betrieb von Sporteinrichtungen
R93.1.2 - Aktivitäten von Sportvereinen
R93.1.3 - Fitnesseinrichtungen
R93.1.9 - Sonstige sportliche Tätigkeiten
R93.2 - Erbringung von Unterhaltungs- und Freizeitdienstleistungen
R93.2.1 - Tätigkeiten von Vergnügungs- und Themenparks
R93.2.9 - Sonstige Tätigkeiten von Unterhaltungs- und Freizeitdienstleistungen
S - Erbringung von sonstigen Dienstleistungen
S94 - Tätigkeiten von Mitgliederorganisationen
S94.1 - Wirtschafts-, Arbeitgeber- und Berufsverbände
S94.1.1 - Wirtschafts- und Arbeitgeberverbände
S94.1.2 - Berufsverbände
S94.2 - Gewerkschaften
S94.2.0 - Gewerkschaften
S94.9 - Sonstige Mitgliederorganisationen
S94.9.1 - Kirchliche Vereinigungen
S94.9.2 - Politische Vereinigungen
S94.9.9 - Sonstige Mitgliederorganisationen, ang
S95 - Reparatur von Computern und persönlichen und Haushaltsgegenständen
S95.1 - Reparatur von Computern und Kommunikationsgeräten
S95.1.1 - Reparatur von Computern und Peripheriegeräten
S95.1.2 - Reparatur von Kommunikationsgeräten
S95.2 - Reparatur von persönlichen und Haushaltsgegenständen
S95.2.1 - Reparatur von Unterhaltungselektronik
S95.2.2 - Reparatur von Haushaltsgeräten und Haus- und Gartengeräten
S95.2.3 - Reparatur von Schuhen und Lederwaren
S95.2.4 - Reparatur von Möbeln und Einrichtungsgegenständen
S95.2.5 - Reparatur von Uhren und Schmuck
S95.2.9 - Reparatur von sonstigen persönlichen Gegenständen und Haushaltsgegenständen
S96 - Erbringung sonstiger persönlicher Dienstleistungen
S96.0 - Erbringung sonstiger persönlicher Dienstleistungen
S96.0.1 - Waschen und (chemische) Reinigen von Textil- und Pelzwaren
S96.0.2 - Friseur- und sonstige Schönheitspflege
S96.0.3 - Bestattungsgewerbe und damit verbundene Tätigkeiten
S96.0.4 - Erbringung körperlicher Dienstleistungen
S96.0.9 - Erbringung sonstiger persönlicher Dienstleistungen ang
T - Tätigkeiten von privaten Haushalten als Arbeitgeber; Undifferenzierte Güter- und Dienstleistungstätigkeiten privater Haushalte für den Eigenbedarf
T97 - Tätigkeiten privater Haushalte als Arbeitgeber von Hauspersonal
T97.0 - Tätigkeiten privater Haushalte als Arbeitgeber von Hauspersonal
T97.0.0 - Tätigkeiten privater Haushalte als Arbeitgeber von Hauspersonal
T98 - Undifferenzierte Güter- und Dienstleistungstätigkeiten privater Haushalte für den Eigenbedarf
T98.1 - Undifferenzierte Güterproduktionstätigkeiten privater Haushalte für den Eigenbedarf
T98.1.0 - Undifferenzierte Güterproduktionstätigkeiten privater Haushalte für den Eigenbedarf
T98.2 - Undifferenzierte Dienstleistungstätigkeiten privater Haushalte für den Eigenbedarf
T98.2.0 - Undifferenzierte Dienstleistungstätigkeiten privater Haushalte für den Eigenbedarf
U - Tätigkeiten extraterritorialer Organisationen und Körperschaften
U99 - Tätigkeiten extraterritorialer Organisationen und Körperschaften
U99.0 - Aktivitäten extraterritorialer Organisationen und Körperschaften
U99.0.0 - Aktivitäten extraterritorialer Organisationen und Körperschaften
"""

def get_parent_code(code):
    """
    Determines the parent code of a given NACE code.
    For example:
    - 'A1.1.1' -> 'A1.1'
    - 'A1.1' -> 'A1'
    - 'A1' -> 'A'
    - 'A' -> None
    """
    if '.' in code:
        return '.'.join(code.split('.')[:-1])
    else:
        # Remove the last character (number) to find the parent
        return code[:-1] if len(code) > 1 else None

def build_nace_hierarchy(data):
    """
    Builds a hierarchical dictionary from NACE codes.
    """
    code_map = {}
    roots = []
    output = {}
    # First pass: create all nodes
    for line in data.strip().split('\n'):
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        # if ' - ' not in line:
        #     continue  # Skip lines without proper formatting
        code, description = line.split(' - ', 1)
        output[code] = description
    #     code_map[code] = {
    #         'code': code,
    #         'description': description,
    #         'children': []
    #     }

    # # Second pass: assign children to parents
    # for code, node in code_map.items():
    #     parent_code = get_parent_code(code)
    #     if parent_code and parent_code in code_map:
    #         code_map[parent_code]['children'].append(node)
    #     else:
    #         roots.append(node)

    return output

def main():
    # Build the hierarchical structure
    nace_hierarchy = build_nace_hierarchy(nace_data_dutch)

    # Output the JSON to a file
    with open('./data/nace_codes_object_du.json', 'w', encoding='utf-8') as f:
        json.dump(nace_hierarchy, f, ensure_ascii=False, indent=2)

    print("NACE hierarchy has been successfully written to 'nace_codes_object.json'.")

if __name__ == "__main__":
    main()
