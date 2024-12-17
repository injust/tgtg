from __future__ import annotations

archived: set[int] = {
    # Evana Patisserie & Cafe
    791287,  # Beautiful Pastries
    # HiFruit Technology Inc. - Scarborough
    127548404736019393,  # Royal Jasmine Rice 皇家香米
    # Kin-Kin Bakery (Agincourt Mall)
    507834,  # Surprise Bag
    # La Rocca Creative Kitchen
    379533,  # Cakes
    # La Rocca Creative Kitchen
    505340,  # Cakes
    # Marché Leo's Market - North York
    376415,  # Assorted Dry Items
    # McEwan Fine Foods (Don Mills) - SUSHI
    89306236213788353,  # $30 Surprise Bag
    89071801115092961,  # $24 Surprise Bag
    # NUBON MARKET
    82906386258609857,  # Groceries
    # Rose's Chester Fried Chicken
    519782,  # Assorted Fried Chicken & Filipino Foods
    # Sing Bakery
    766896,  # Bread Bag
    # Sugar N Spice
    1350295,  # Baked Goods
    # Sushi Shop - Union Station
    121403951647965025,  # Surprise Bag
    # Taste Good BBQ
    649873,  # BBQ and Chinese food
}

disabled: set[int] = {
    # Bake Code (Midland Ave.) - Scarborough
    646160,  # Baked Goods
    # Chocolat de Kat
    537465,
    # Ensanemada
    633196,  # Surprise Bag
}

east_york: set[int] = {
    # LaRochelle Confections Inc.
    518221,  # Surprise Bag
    # United Craft
    144211782586040609,  # Craft Beer, Cider & Cocktail Mixer Pack
    142000577808538561,  # Mixed Radlers Surprise Bag
}

far: set[int] = {
    # 100 King st West Calii Love - 100 King Street
    769232,  # Calii Love Surprise Bag
    906034,  # Fresh After Lunch Surprise Bag
    129606116422699073,  # Surprise Bowl
    # 367 King St. West Calii Love - 367 King St. West
    101166256283263041,  # Calii Love Surprise Bag
    101538797854932737,  # Surprise bowl
    129604617437781121,  # Surprise Bowl
    # A Tavola
    82874509545092577,  # Surprise Bag
    # Amber Kitchen and Coffee
    123793163840686273,  # Baked goods and Sandwiches Surprise Bag
    # Amelia’s Market  # noqa: RUF003
    66353292298537505,  # $15 Surprise Bag : Grab and go food
    86148719765039329,  # Baked goods
    # Augusta Coffee Bar
    151657734659345249,  # Test Roast Coffee
    # Aunt Beth Bakes
    940373,  # Whiskey Cookie Surprise Bag
    # Baegopa
    130253110312280961,  # Surprise Cupbop
    # Basil Box - Royal Bank Plaza
    515772,  # Surprise bag
    # Basil Box - Toronto General
    1174455,  # Surprise bag
    # Basil Box - Toronto Metropolitan University (formerly Ryerson)
    505530,  # Surprise Bag
    138037670831429409,  # Sip Sip yogurt drink
    # Basil Box - Yonge and Finch
    506278,  # Surprise bag
    # Bingz Crispy Burger 西少爷肉夹馍 - CF Fairview Mall
    1076410,  # Surprise Bag!
    43839166580614081,  # Surprise Bag (L)
    # BKookies Cafe
    82076261892347489,  # Baked goods
    # bloomer's - Bayview
    1296083,  # Surprise bag
    # bloomer's - Bloor West
    1296080,  # Surprise Bag
    # bloomer's - Queen St
    1296132,  # Surprise bag
    # Burukudu Coffee
    941219,  # Assorted Coffee Beans Large
    1274072,  # Surprise Coffee
    # Cafe Our Hours
    1299996,  # Surprise Bag
    # California Sandwiches (Warden Ave.)
    632267,  # Prepared Meals
    # Castella King余味古早
    137730298417516065,  # Baked goods
    # Cheese Baker
    378920,  # Surprise Bag
    # CHO-KWOK-LAT
    506931,  # Surprise bag
    # ChocoSol
    907694,  # Chocolate Surprise
    1170829,  # Coffee rations
    1208932,  # Surprise Bag dark chocolate
    1271741,  # Unsweetened Chocolate
    48422911068547233,  # Chocolate and Spice Suprise!!
    # ChocoSol's Chocolate Bar & Boutique
    65195503724749217,  # Chocolate Surprise
    65201763237996257,  # Dark Chocolate Surprise Bag
    65209425391474465,  # Coffee Rations
    # Chop Hop - Temperance
    49001479148365569,  # Surprise Bag
    # Circles & Squares Bakery Café - North York
    1076222,  # Suprise bag
    # Circles & Squares Bakery Café - Yonge St
    1408783,  # Surprise bag
    # CKTL & Co.
    82669232185585921,  # Surprise Dinner Bag
    # Courage Cookies - Dundas Street West
    648110,  # Cookies!
    # Courage Cookies - Stackt Market
    633174,  # Cookies!
    # CRUMBS GOURMET PATTIES
    508884,  # Surprise Bag
    # Deer Cake - Markham
    1029354,  # Large Surprise Bag
    1029366,  # Surprise Bag - Toast Box/Baked Goods 冰面包吐司
    1029388,  # Surprise Bag
    # Delicious Empanadas - Dufferin St
    378983,  # $15 Value Meal
    1274040,  # $15 Value
    # Delicious Empanadas Latin Cafe
    1655516,  # Surprise Bag
    # Dolce & Gourmando - North York
    1025784,  # Big Goody Bag
    943892,  # Goody Bag
    # Eataly - Yorkville
    370413,  # Assorted Prepared Foods
    370421,  # Baked Goods
    379625,  # Charcuterie Items
    769120,  # Assorted Pantry Items
    1703451,  # Pastry
    # Filosophy Pastry and Espresso Bar
    1451690,  # Surprise Bag
    # Fruitful Market
    1659970,  # Surprise bag
    # GG Sushi/Paku Foods
    126130613638166529,  # Surprise Bag 1
    133105633950740001,  # Surprise Bag 2
    # Goûter (Eglinton West)
    632623,  # Surprise Bag
    144393095525720609,  # Frozen Baked Goods
    # Green Press - Bloor - 3
    508614,  # Surprise Bag
    # Greenhouse Juice - Brookfield Place
    631189,  # Assorted Items
    # Greenhouse Juice - Forest Hill
    234980,  # Assorted Items
    80010988711186273,  # Surprise Bag
    # Greenhouse Juice - Macpherson
    234974,  # Assorted Items
    # Greenhouse Juice - Queen West
    234968,  # Assorted Items
    114246763815273761,  # Surprise Bag
    122326876508919681,  # Surprise Bag
    # Greenhouse Juice - St. Clair
    234975,  # Assorted Items
    # Greenhouse Juice - Union Station
    372839,  # Assorted Items
    # Hattendo 八天堂 - Baldwin Village
    1078202,  # Surprise Bag of Heavenly Pastries
    # Hattendo 八天堂 - Holt Renfrew Centre
    1077232,  # Surprise Bag of Heavenly Pastries
    # Hattendo 八天堂 - Markham
    1078203,  # Surprise Bag of Heavenly Pastries
    # Healthy Planet - East Scarborough
    131641842590169441,  # Assorted Grocery Items
    131642299748345057,  # Assorted Meat Bag
    133356484787645953,  # Mixed Surprise Bag
    # Healthy Planet - Markham
    43736154582160833,  # Meat Bag
    43736154850595201,  # Assorted Grocery Items
    71052614717172353,  # Mixed Surprise Bag
    # Healthy Planet - South Scarborough
    131641610741613633,  # Assorted Grocery Items
    131642275442355681,  # Assorted Meat Bag
    135990011133131041,  # Mixed Surprise Bag
    # Hunter Coffee Shop
    77120517535223969,  # Small Surprise Bag
    77121184228232545,  # Large Surprise Bag
    # IKEA - North York
    14165470828971393,  # Morning Surprise Bag
    14166701768430177,  # Dinner Surprise Bag
    # IKEA - Toronto Downtown
    14165503645195489,  # Morning Surprise Bag
    14166714452012257,  # Dinner Surprise Bag
    # Kafe Dáki
    908330,  # Baked goods bag
    # Kajun Chicken & Seafood - Kingston Rd
    33654749134141825,  # Surprise Bag
    # Kingston 12 Patty Shop
    20317924928427073,  # Patty Surprise Bag
    # Kingston 12 Patty Shop - Dundas
    102949654161238177,  # Surprise Bag
    # Kingyo Fisherman's Market
    765532,  # Gourmet Grocery Surprise Bag
    # Kitten and the Bear
    508137,  # Surprise Bag
    # La Rocca Creative Kitchen
    505336,  # Cupcakes and assorted baked goods
    1562890,  # Small Cake
    # Le Petit Pain
    84881982995506529,  # Freshly Baked Breads and Pastries
    # Let's Soup
    515988,  # Surprise Bag
    # Levetto
    766633,  # Italian Surprise Bag
    # Longo's - Yonge & Sheppard
    518631,  # Baked Goods
    518632,  # Prepared Foods
    # Maki Mart North York - North York
    10193768865923073,  # Surprise bag $24
    18056633890926273,  # Surprise Bag $21
    38051446410598721,  # Maki Surprise Bag
    130549138385254433,  # Hand Roll Surprise Bag!
    # Maman
    375980,  # Surprise Bag
    # Manal Bashir Pastry Co.
    1208268,  # Baked goods
    # Mr. Kane - Natural Juices & Exotic Fruits
    20617615905913633,  # Surprise Bag
    20757178189865601,  # Groceries
    # NEO COFFEE BAR - BAY X COLLEGE
    109319395122922273,  # $15 Baked Goods Surprise Bag
    109319617108027329,  # $18 Baked Goods Surprise Bag
    109319822136619713,  # $21 Baked Goods Surprise Bag
    109320019805791649,  # $24 Baked Goods Surprise Bag
    # NEO COFFEE BAR - FREDERICK X KING
    107822979170092257,  # $15 Baked Goods Surprise Bag
    107823380648857921,  # $18 Baked Goods Surprise Bag
    107823615831884417,  # $21 Baked Goods Surprise Bag
    107823981556765249,  # $24 Baked Goods Surprise Bag
    # NEO COFFEE BAR - KING X SPADINA
    109316693074179745,  # $15 Baked Goods Surprise Bag
    109316859582255745,  # $18 Baked Goods Surprise Bag
    109317014972845153,  # $21 Baked Goods Surprise Bag
    109317163417651649,  # $24 Baked Goods Surprise Bag
    # NEO COFFEE BAR - PATH - The Path
    95706794378853985,  # $21 Baked Goods Surprise Bag
    103756586095630145,  # $24 Baked Goods Surprise Bag
    110817640475830689,  # $15 Baked Goods Surprise Bag
    110818097960459201,  # $18 Baked Goods Surprise Bag
    # NEO COFFEE BAR - YONGE X GLOUCESTER
    109328406333402113,  # $15 Baked Goods Surprise Bag
    109328583254905409,  # $18 Baked Goods Surprise Bag
    109328751709169697,  # $21 Baked Goods Surprise Bag
    109328887962726177,  # $24 Baked Goods Surprise Bag
    # Newport Fish & Seafood
    505676,  # Surprise Bag
    # NUTTEA Toronto - 637 Bloor St W
    1406942,  # Tea Surprise Bag
    105257928138595425,  # NUTTEA Surprise Bag
    # Petti Fine Foods
    649777,  # Medium Bag
    # Pusateri's - Avenue Rd
    373762,  # Baked Goods
    379051,  # Prepared Foods
    1078618,  # Pantry & General Grocery items
    # Rahier Patisserie
    509030,  # Bread and Pastries Surprise Bag
    1171586,  # Small Cake or Tarts
    1560990,  # Quiche Bag
    # Rancho Relaxo To Go
    515775,  # Surprise Bag
    # Ruru Baked
    907452,  # Surprise Bag
    90751616844449665,  # Surprise Bag - Ice Cream + Baked Goods
    103253956677685665,  # Surprise Bag - Ice Cream Pints
    # Saving Gigi
    372245,  # Surprise Bag
    # Soma Bone Broth Co.
    509518,  # Surprise Bag
    # Subtext Coffee
    518861,  # Large Surprise Bag
    1563057,  # Baked goods
    # Summerhill Market - Annex
    376441,  # Prepared Foods
    # Summerhill Market - Forest Hill
    376660,  # Prepared Foods
    # Sushi Real Fruit
    516525,  # Sushi Surprise Bag
    # The Bake House - Markham
    62327179096036001,  # Surprise Bag
    66416703558784641,  # Surprise Bag (Frozen)
    97412266903335329,  # Ice Cream Cake!
    # The Night Baker - College
    515273,  # Assorted Cookies
    # The Night Baker - Danforth
    515081,  # Assorted Cookies
    # The Pantry Fine Cheese
    791270,  # Surprise Bag
    # The Pie Commission
    1703444,  # Surprise bag
    # Tobiko Sushi
    649370,  # Sushi Surprise Bag
    # Tre Mari Bakery
    646010,  # Prepared Meals and Baked Goods
    1077771,  # Assorted Cannoli Bag
    # Urla Fine Foods
    940390,  # Surprise Bag
    # Village Juicery - Bloor St
    372812,  # Prepared Juices + Food
    # Village Juicery - Danforth
    373581,  # Prepared Juices + Food
    # Village Juicery - Spadina
    372813,  # Prepared Juices + Food
    # Whole Foods - ON - Unionville
    73322727368288545,  # Bakery Bag
    73340264039378913,  # Prepared Foods Bag
    # Whole Foods - ON - Yonge & Sheppard
    73322730623061985,  # Bakery Bag
    73340268166558753,  # Prepared Foods Bag
    # XCAKE 隨心意 - Markham
    38053218033566113,  # Surprise Bag (M)
    # Zoomys Juicery - Pape
    27622358334157409,  # Surprise Bag 2
    # 台客赞 Aitaiker Taiwanese Fried Chicken - Richmond Hill
    1489887,  # Surprise Bag (S)
}

filipino: set[int] = {
    # Coffee In
    1296955,  # Surprise Bag
    # Manyaman Foods Filipino Cuisine - Scarborough
    34300334078310337,  # Surprise Bag
    # Tagpuan - College St
    1454297,  # Evening Surprise Bag
    87047176813977313,  # Surprise Bag
    119702167645600225,  # Desserts !
    # Tagpuan - Yonge st
    122045877528868801,  # Evening Surprise Bag
    122047137732662049,  # Surprise Bag
    # Tagpuan (Van Horne Ave)
    941790,  # Evening Surprise Bag
}

flowers: set[int] = {
    # Ginkgo Floral Design - Toronto
    137397239898904097,  # Flower Surprise Bag
    # GTA Florist - North York
    141190505436669761,  # Flower Surprise Bag
    # Hills Florist - Toronto
    123180518470945697,  # Surprise Bouquet of Flowers
    133352804839546049,  # Surprise Large Bouquet of Flowers
    # Kakazan - Toronto
    125267972601511585,  # Standard Flower Surprise Bag
    127000297739870177,  # Mini Flower Surprise Bag
    127578450584258593,  # Flowers & plants
    132846093458009377,  # Mini florist pick bouquet
    # Lou-Lou's Flower Truck
    1561525,  # Flower Surprise bag
}

jtown: set[int] = {
    # Bakery Nakamura - Markham
    1274244,  # Baked goods
    1406748,  # Half whole cake
    1408604,  # Pastry goods
    # La Petite Colline
    505184,  # Baked Goods Surprise Bag
    127055692199864673,  # Baked goods
}

late: set[int] = {
    # Kung Fu Tea - Broadview
    88553512050558529,  # Surprise Bag
    # Kung Fu Tea - Downtown - Wellesley on Yonge
    377151,  # Surprise Bag
}

rosedale: set[int] = {
    # Rosedale's Finest Specialty Foods
    909343,  # Large Surprise Bag
    942190,  # Regular Surprise Bag
    # Summerhill Market - Rosedale
    371532,  # Prepared Foods
}

tien: set[int] = {
    # ABURI TORA - Yorkdale Mall
    630348,  # Surprise Bag
    # CHICHA San Chen 吃茶三千 (Ossington)
    88420443877014497,  # Surprise Bag
    # Goûter (Bathurst)
    647660,  # Surprise Bag
    144387140118235201,  # Frozen Baked Goods
    # im mochi
    50994187116261217,  # Donuts
    # Kin-Kin Bakery (Yonge Sheppard Centre)
    507832,  # Surprise Bag
    # Nadege Patisserie - Bloor-Annex
    631882,  # Surprise bag - Large
    631883,  # Surprise bag - Small
    631884,  # Extra Large Baked/ Cake Goods Surprise Bag
    # Nadege Patisserie - Queen West
    372476,  # Small Baked/ Cake Goods Surprise Bag
    377764,  # Large Baked/ Cake Goods Surprise Bag
    378051,  # Extra Large Baked/ Cake Goods Surprise Bag
    # Nadege Patisserie - Rosedale
    507476,  # Surprise bag - Small
    507477,  # Extra Large Baked/ Cake Goods Surprise Bag
    507468,  # Surprise bag - Large
    # Nonna Lia - Oakwood
    85792504166058433,  # Single Dessert Bag
    85794643630215137,  # Double Dessert Bag
    96872852823024801,  # Assorted Surprise Bag
    99180077308855521,  # Double Sandwich Bag
    125208606788673473,  # Lasagna Surprise Bag
    # Tao Tea Leaf - Union Station
    631173,  # Night Surprise Bag
}

ignored: set[int] = set()

inactive: set[int] = {
    # A Tavola
    102924490584841441,  # Spatchcock Chicken
    133680772668116737,  # Moroccan Cassoulet
    133681571800480801,  # Chana Masala
    133682084478622145,  # Chicken Cacciatore
    134504385263558209,  # Gnocchi for two
    # Allan's Pastry Shop
    80904526670816225,  # Baked goods
    83557259883829633,  # Baked goods Large
    # Bake Code (Yonge St.) - North York
    374970,  # Surprise Bag
    # Bake Code Croissanterie (Yonge St.) - Toronto
    374611,  # Surprise Bag
    # Basil Box - Royal Bank Plaza
    1408726,  # Large Surprise Bag
    1451142,  # Drinks Bag
    # Bingz Crispy Burger 西少爷肉夹馍 - CF Fairview Mall
    114343305084580097,  # Surprise Bag (M)
    129979491769785025,  # Surprise Bag
    130566897720402529,  # Surprise Bag
    133164919834302017,  # Surprise Bag
    134619428856585825,  # Surprise Bag
    140418960464062113,  # Surprise Bag
    # Bingz Crispy Burger 西少爷肉夹馍 - Eaton Center
    36249191346825633,  # Surprise Bag
    43837672200426849,  # Surprise Bag （L）  # noqa: RUF003
    # Burukudu Coffee
    941206,  # Assorted coffee beans
    # Castella King余味古早
    137453254494413825,  # Baked goods
    138036037579678369,  # Baked goods
    # CKTL & Co.
    125607437675540929,  # Steak & Fried potatoes
    125599044091616641,  # Steak - Salad/fries
    109008316791490785,  # Baked goods
    108156140017939233,  # Baked goods
    101822558454214785,  # Baked goods
    100104630345635297,  # Surprise Bag
    # Courage Cookies - Dundas Street West
    37959769041115585,  # Cookie Dough
    # Daan Go Cake Lab - Scarborough
    518250,  # Surprise Bag Medium
    518251,  # Surprise Bag Large
    # Delicious Empanadas - Dufferin St
    131924680033894145,  # $18 Value
    # Eataly - Yorkville
    374329,  # Pasta Kit
    # HiFruit Technology Inc. - Scarborough
    11913019614429185,  # Grapefruit Box 爆汁葡萄柚盲盒
    # Kung Fu Tea - Broadview
    1485596,  # Surprise Bag
    # Le Gourmand - Brookfield Place
    1170771,  # Surprise Bag
    # Le Gourmand - Spadina
    1170772,  # Surprise Bag
    # Maki Mart North York - North York
    129400934899261121,  # Hand Roll Surprise Bag
    # Marché Leo's Market - North York
    376665,  # Prepared Items
    # Metro - 16 William Kitchen Rd
    1354060,  # Assorted Meat
    # Moge & Mofu
    790645,  # Bubble Tea and/or Baked Goods
    # Petti Fine Foods
    634283,  # Large Bag
    649674,  # Small Bag
    # The Smoke Bloke Smoked Salmon and Fine Smoked Foods
    646846,  # Small Surprise Bag
    # Subtext Coffee
    518854,  # Small Surprise Bag
    # Sugar N Spice
    1350245,  # Baking Groceries
    # Tagpuan - Yonge st
    122047724947037185,  # Dessert Surprise
    # Tao Tea Leaf - Union Station
    646186,  # Mid-day Surprise Bag
    # Torch GG Sushi - Downtown
    371930,  # Surprise Bag
    # YUBU - Scarborough - Skycity Mall
    1353655,  # Surprise Bag
    # 台客赞 Aitaiker Taiwanese Fried Chicken - Richmond Hill
    1489885,  # Surprise Bag (L)
    135229962935649857,  # Surprise Bag (S)
}

tracked: set[int] = {
    # Cakeview Bakery & Cafe
    649947,  # Bread
    649979,  # Cake
    # Choo Tea 初代茶铺
    131695360086499809,  # Bubble Tea Surprise Bag
    # Daan Go Cake Lab - Scarborough
    376271,  # Surprise Bag Small
    # Eataly - Don Mills
    48448666821020353,  # Baked Goods
    48448667190123489,  # Assorted Prepared Foods
    48448668062525921,  # Charcuterie Items
    48448668767184353,  # Assorted Pantry Items
    # Food Basics - 1571  Sandhurst Cir
    144138957721499713,  # Meat & Seafood Surprise Bag
    # Francesca Bakery - 1
    1209374,  # Surprise Bag
    # IKI Shokupan - Richmond Hill
    41210055715544609,  # Baked Goods Surprise Bag
    # LÀ LÁ Bakeshop - Scarborough
    1561993,  # Surprise Bag
    # La Rocca Creative Kitchen
    374252,  # Cupcakes and assorted baked goods
    # McEwan Foods - Don Mills
    377070,  # Surprise Bag
    # Metro - 1050 Don Mills Rd
    943701,  # Assorted Fruit & Salad
    1299767,  # Assorted Meat
    99712944450874561,  # Deli Surprise Bag
    # Metro - 2900 Warden Ave
    1354049,  # Assorted Meat
    # Nonna Lia - Oakwood
    85795141007552961,  # 6-Inch Cake Bag
    85795389478113761,  # 8-Inch Cake Bag
    85795679891750113,  # 10-Inch Cake Bag
    # The Night Baker - North York
    81417090592535617,  # Assorted Cookies
    # The Smoke Bloke Smoked Salmon and Fine Smoked Foods
    631121,  # Large Surprise Bag
    631574,  # Medium Surprise Bag
    # TYCOON TOFU - Pacific Mall - 2nd Floor in Pacific Heritage Town
    114202587358750689,  # Surprise Bag
    139511384051493185,  # Surprise Bag
    140068886400994849,  # Surprise Bag
    # Village Juicery - Yonge St
    378034,  # Prepared Juices + Food
    # Wellvis Health Nutrition
    135951121448163521,  # Protein Surprise Bag
    142338893572138881,  # Vitamin Surprise Bag
    142341292533196417,  # Greens Powder Surprise Bag
}
