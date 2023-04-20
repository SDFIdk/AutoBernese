import datetime as dt

import yaml

from ab import pkg
from ab.sta import (
    STA_created_timestamp,
    build_receiver_no,
    country_code,
)


def test_country_code():
    test_data = (
        # Function expects correctly formatted country names
        ("Denmark", "DNK"),
        ("France", "FRA"),
        ("Italy", "ITA"),
        # Country names are trimmed
        ("  Denmark ", "DNK"),
        ("  France ", "FRA"),
        ("  Italy ", "ITA"),
        # Function does not fix spelling mistakes
        ("denmark", None),
        ("france", None),
        ("italy", None),
        ("Neverland", None),
        ("Narnia", None),
        ("Madeuparupa", None),
    )
    for country_name, expected in test_data:
        result = country_code(country_name)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    test_data_full = yaml.safe_load(pkg.country_codes.read_text())
    for country_name, expected in test_data_full.items():
        result = country_code(country_name)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_STA_created_timestamp():
    d = dt.datetime(2023, 3, 15, 13, 50)
    expected = "15-MAR-23 13:50"
    result = STA_created_timestamp(d)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."


def test_build_receiver_no():
    test_data = (
        ("146", "146"),
        ("159", "159"),
        ("175", "175"),
        ("211", "211"),
        ("222", "222"),
        ("223", "223"),
        ("224", "224"),
        ("225", "225"),
        ("242", "242"),
        ("251", "251"),
        ("471", "471"),
        ("530", "530"),
        ("640", "640"),
        ("995", "995"),
        ("0375", "375"),
        ("0386", "386"),
        ("1302", "1302"),
        ("1436", "1436"),
        ("1504", "1504"),
        ("1699", "1699"),
        ("1863", "1863"),
        ("2090", "2090"),
        ("2185", "2185"),
        ("3057", "3057"),
        ("3482", "3482"),
        ("T196", "196"),
        ("T200", "200"),
        ("T295", "295"),
        ("T314", "314"),
        ("T318", "318"),
        ("T319", "319"),
        ("T344", "344"),
        ("T394", "394"),
        ("00001", "1"),
        ("00008", "8"),
        ("00009", "9"),
        ("00113", "113"),
        ("00177", "177"),
        ("00196", "196"),
        ("00224", "224"),
        ("00396", "396"),
        ("00450", "450"),
        ("00451", "451"),
        ("00494", "494"),
        ("00802", "802"),
        ("01151", "1151"),
        ("01153", "1153"),
        ("01155", "1155"),
        ("01163", "1163"),
        ("01164", "1164"),
        ("01168", "1168"),
        ("01180", "1180"),
        ("01219", "1219"),
        ("01235", "1235"),
        ("01308", "1308"),
        ("01585", "1585"),
        ("01587", "1587"),
        ("01589", "1589"),
        ("01902", "1902"),
        ("02042", "2042"),
        ("02044", "2044"),
        ("02046", "2046"),
        ("02259", "2259"),
        ("02347", "2347"),
        ("02412", "2412"),
        ("02466", "2466"),
        ("02539", "2539"),
        ("02540", "2540"),
        ("02631", "2631"),
        ("02797", "2797"),
        ("02811", "2811"),
        ("02812", "2812"),
        ("02813", "2813"),
        ("02858", "2858"),
        ("02859", "2859"),
        ("02870", "2870"),
        ("02880", "2880"),
        ("02884", "2884"),
        ("02887", "2887"),
        ("02904", "2904"),
        ("02905", "2905"),
        ("03176", "3176"),
        ("03888", "3888"),
        ("03909", "3909"),
        ("04030", "4030"),
        ("04116", "4116"),
        ("04125", "4125"),
        ("04261", "4261"),
        ("04321", "4321"),
        ("04579", "4579"),
        ("04580", "4580"),
        ("05139", "5139"),
        ("08024", "8024"),
        ("09384", "9384"),
        ("10469", "10469"),
        ("11106", "11106"),
        ("11108", "11108"),
        ("12104", "12104"),
        ("12109", "12109"),
        ("12110", "12110"),
        ("17110", "17110"),
        ("17560", "17560"),
        ("17997", "17997"),
        ("17999", "17999"),
        ("18023", "18023"),
        ("18091", "18091"),
        ("18424", "18424"),
        ("18643", "18643"),
        ("18760", "18760"),
        ("18964", "18964"),
        ("20207", "20207"),
        ("20328", "20328"),
        ("20329", "20329"),
        ("21043", "21043"),
        ("21045", "21045"),
        ("21438", "21438"),
        ("21512", "21512"),
        ("21519", "21519"),
        ("21525", "21525"),
        ("22774", "22774"),
        ("22992", "22992"),
        ("23155", "23155"),
        ("23227", "23227"),
        ("23229", "23229"),
        ("24969", "24969"),
        ("251-U", "251"),
        ("26987", "26987"),
        ("26990", "26990"),
        ("27294", "27294"),
        ("28641", "28641"),
        ("28746", "28746"),
        ("28748", "28748"),
        ("30002", "30002"),
        ("30098", "30098"),
        ("30100", "30100"),
        ("30190", "30190"),
        ("31732", "31732"),
        ("32256", "32256"),
        ("32257", "32257"),
        ("32552", "32552"),
        ("32572", "32572"),
        ("32811", "32811"),
        ("32872", "32872"),
        ("32887", "32887"),
        ("34262", "34262"),
        ("35438", "35438"),
        ("36693", "36693"),
        ("40016", "40016"),
        ("41644", "41644"),
        ("43911", "43911"),
        ("48002", "48002"),
        ("50003", "50003"),
        ("50017", "50017"),
        ("50860", "50860"),
        ("57134", "57134"),
        ("61372", "61372"),
        ("64043", "64043"),
        ("70005", "70005"),
        ("70408", "70408"),
        ("71845", "71845"),
        ("80040", "80040"),
        ("80042", "80042"),
        ("80044", "80044"),
        ("80048", "80048"),
        ("80049", "80049"),
        ("80240", "80240"),
        ("80244", "80244"),
        ("80278", "80278"),
        ("80282", "80282"),
        ("80354", "80354"),
        ("96517", "96517"),
        ("96523", "96523"),
        ("CR325", "325"),
        ("T 351", "351"),
        ("T 393", "393"),
        ("T 408", "408"),
        ("T-171", "171"),
        ("T-174", "174"),
        ("T-237", "237"),
        ("T-238", "238"),
        ("T-321", "321"),
        ("T-413", "413"),
        ("000113", "113"),
        ("019354", "19354"),
        ("136795", "136795"),
        ("351087", "351087"),
        ("352031", "352031"),
        ("352123", "352123"),
        ("352253", "352253"),
        ("352269", "352269"),
        ("352420", "352420"),
        ("355045", "355045"),
        ("355290", "355290"),
        ("355316", "355316"),
        ("355317", "355317"),
        ("355322", "355322"),
        ("355355", "355355"),
        ("355365", "355365"),
        ("355368", "355368"),
        ("355409", "355409"),
        ("355437", "355437"),
        ("355486", "355486"),
        ("355523", "355523"),
        ("355611", "355611"),
        ("355615", "355615"),
        ("355802", "355802"),
        ("355832", "355832"),
        ("355837", "355837"),
        ("355904", "355904"),
        ("355913", "355913"),
        ("355916", "355916"),
        ("355918", "355918"),
        ("355939", "355939"),
        ("356103", "356103"),
        ("356151", "356151"),
        ("356166", "356166"),
        ("356236", "356236"),
        ("356249", "356249"),
        ("356332", "356332"),
        ("356337", "356337"),
        ("356365", "356365"),
        ("356373", "356373"),
        ("356468", "356468"),
        ("356474", "356474"),
        ("356510", "356510"),
        ("356521", "356521"),
        ("356529", "356529"),
        ("356532", "356532"),
        ("356534", "356534"),
        ("356576", "356576"),
        ("356577", "356577"),
        ("356582", "356582"),
        ("356583", "356583"),
        ("356609", "356609"),
        ("356686", "356686"),
        ("451105", "451105"),
        ("451111", "451111"),
        ("451115", "451115"),
        ("452176", "452176"),
        ("452503", "452503"),
        ("453657", "453657"),
        ("453661", "453661"),
        ("454401", "454401"),
        ("455691", "455691"),
        ("455989", "455989"),
        ("456391", "456391"),
        ("456402", "456402"),
        ("457127", "457127"),
        ("457881", "457881"),
        ("459187", "459187"),
        ("459348", "459348"),
        ("460017", "460017"),
        ("460019", "460019"),
        ("460027", "460027"),
        ("460033", "460033"),
        ("461525", "461525"),
        ("462575", "462575"),
        ("462577", "462577"),
        ("462582", "462582"),
        ("462583", "462583"),
        ("495219", "495219"),
        ("495308", "495308"),
        ("495328", "495328"),
        ("495369", "495369"),
        ("495521", "495521"),
        ("495524", "495524"),
        ("496017", "496017"),
        ("496581", "496581"),
        ("496604", "496604"),
        ("496975", "496975"),
        ("496988", "496988"),
        ("701077", "701077"),
        ("CR 320", "320"),
        ("CR 321", "321"),
        ("LE2998", "2998"),
        ("LE4687", "4687"),
        ("T 408U", "408"),
        ("T-313U", "313"),
        ("T-398U", "398"),
        ("0020391", "20391"),
        ("0032552", "32552"),
        ("0038794", "38794"),
        ("0038948", "38948"),
        ("0080143", "80143"),
        ("0080144", "80144"),
        ("0080167", "80167"),
        ("1700062", "700062"),
        ("1700065", "700065"),
        ("1700277", "700277"),
        ("1700509", "700509"),
        ("1700697", "700697"),
        ("1700707", "700707"),
        ("1700871", "700871"),
        ("1700963", "700963"),
        ("1700979", "700979"),
        ("1700988", "700988"),
        ("1701078", "701078"),
        ("1703208", "703208"),
        ("1704024", "704024"),
        ("1705338", "705338"),
        ("1705339", "705339"),
        ("1705353", "705353"),
        ("1705359", "705359"),
        ("1705400", "705400"),
        ("1705416", "705416"),
        ("1705430", "705430"),
        ("1705431", "705431"),
        ("1705438", "705438"),
        ("1705441", "705441"),
        ("1705442", "705442"),
        ("1705445", "705445"),
        ("1705533", "705533"),
        ("1705557", "705557"),
        ("1705561", "705561"),
        ("1705596", "705596"),
        ("1705608", "705608"),
        ("1706119", "706119"),
        ("1706436", "706436"),
        ("1706448", "706448"),
        ("1706461", "706461"),
        ("1706532", "706532"),
        ("1706534", "706534"),
        ("1706733", "706733"),
        ("1707020", "707020"),
        ("1708148", "708148"),
        ("1830065", "830065"),
        ("1830091", "830091"),
        ("1830139", "830139"),
        ("1830164", "830164"),
        ("1830169", "830169"),
        ("1830178", "830178"),
        ("1830183", "830183"),
        ("1830189", "830189"),
        ("1830190", "830190"),
        ("1830199", "830199"),
        ("1830200", "830200"),
        ("1830201", "830201"),
        ("1830240", "830240"),
        ("1830243", "830243"),
        ("1830313", "830313"),
        ("1830329", "830329"),
        ("1830344", "830344"),
        ("1830375", "830375"),
        ("1830377", "830377"),
        ("1830391", "830391"),
        ("1830399", "830399"),
        ("1831025", "831025"),
        ("1831037", "831037"),
        ("1831043", "831043"),
        ("1831052", "831052"),
        ("1831110", "831110"),
        ("1831167", "831167"),
        ("1831170", "831170"),
        ("1831175", "831175"),
        ("1831178", "831178"),
        ("1831211", "831211"),
        ("1831235", "831235"),
        ("1831275", "831275"),
        ("1831327", "831327"),
        ("1831537", "831537"),
        ("1831540", "831540"),
        ("1831552", "831552"),
        ("1831577", "831577"),
        ("1831578", "831578"),
        ("1831580", "831580"),
        ("1831581", "831581"),
        ("1831585", "831585"),
        ("1831701", "831701"),
        ("1831703", "831703"),
        ("1831705", "831705"),
        ("1831708", "831708"),
        ("1832285", "832285"),
        ("1833572", "833572"),
        ("1833574", "833574"),
        ("1834194", "834194"),
        ("1834195", "834195"),
        ("1834292", "834292"),
        ("1834302", "834302"),
        ("1834307", "834307"),
        ("1834679", "834679"),
        ("1870146", "870146"),
        ("1870229", "870229"),
        ("1870607", "870607"),
        ("1870627", "870627"),
        ("1870639", "870639"),
        ("1870740", "870740"),
        ("1870864", "870864"),
        ("1871310", "871310"),
        ("1871323", "871323"),
        ("1871480", "871480"),
        ("1871630", "871630"),
        ("1871635", "871635"),
        ("1871896", "871896"),
        ("2001060", "1060"),
        ("2001062", "1062"),
        ("2090088", "90088"),
        ("2090092", "90092"),
        ("2090104", "90104"),
        ("2090126", "90126"),
        ("2090131", "90131"),
        ("2090133", "90133"),
        ("2090222", "90222"),
        ("2090229", "90229"),
        ("3001141", "1141"),
        ("3001288", "1288"),
        ("3001319", "1319"),
        ("3001332", "1332"),
        ("3001376", "1376"),
        ("3002074", "2074"),
        ("3002119", "2119"),
        ("3007887", "7887"),
        ("3009592", "9592"),
        ("3013899", "13899"),
        ("3013909", "13909"),
        ("3015948", "15948"),
        ("3022664", "22664"),
        ("3022730", "22730"),
        ("3022763", "22763"),
        ("3022774", "22774"),
        ("3022890", "22890"),
        ("3023088", "23088"),
        ("3025419", "25419"),
        ("3034615", "34615"),
        ("3046922", "46922"),
        ("3047859", "47859"),
        ("3048221", "48221"),
        ("3057609", "57609"),
        ("3061738", "61738"),
        ("3062184", "62184"),
        ("3069514", "69514"),
        ("3069566", "69566"),
        ("3102220", "102220"),
        ("3228262", "228262"),
        ("3234281", "234281"),
        ("4171758", "171758"),
        ("4171778", "171778"),
        ("4501501", "501501"),
        ("4701366", "701366"),
        ("LP00303", "303"),
        ("LP00839", "839"),
        ("LP00995", "995"),
        ("LP01391", "1391"),
        ("LP01573", "1573"),
        ("LP02295", "2295"),
        ("LP02396", "2396"),
        ("LP02415", "2415"),
        ("LP03169", "3169"),
        ("LP03171", "3171"),
        ("LP03223", "3223"),
        ("LP03373", "3373"),
        ("LP04283", "4283"),
        ("UX50164", "50164"),
        ("UX50168", "50168"),
        ("ZX00115", "115"),
        ("00002095", "2095"),
        ("00002322", "2322"),
        ("00004751", "4751"),
        ("00007361", "7361"),
        ("00009369", "9369"),
        ("00009374", "9374"),
        ("00013697", "13697"),
        ("00017559", "17559"),
        ("00021045", "21045"),
        ("00024908", "24908"),
        ("00026987", "26987"),
        ("00027294", "27294"),
        ("00027311", "27311"),
        ("00028543", "28543"),
        ("00028641", "28641"),
        ("00030152", "30152"),
        ("02862173", "862173"),
        ("20160382", "160382"),
        ("20164659", "164659"),
        ("20297248", "297248"),
        ("235-1757", "351757"),
        ("235-2098", "352098"),
        ("323-0386", "230386"),
        ("220203888", "203888"),
        ("220351863", "351863"),
        ("618-01938", "801938"),
        ("LGGD_0242", "242"),
        # ('not known', '0'),  #  Station BELF in EUREF52.STA back in C.E. 2000.
        ("0220144178", "144178"),
        ("0220177308", "177308"),
        ("0220219865", "219865"),
        ("0220325995", "325995"),
        ("0220348502", "348502"),
        ("0220349584", "349584"),
        ("0220360632", "360632"),
        ("3302A02325", "202325"),
        ("3307A02534", "702534"),
        ("3312A02805", "202805"),
        ("3447A08870", "708870"),
        ("3450A09057", "9057"),
        ("3452A09137", "209137"),
        ("3503A09369", "309369"),
        ("3503A09374", "309374"),
        ("3550A13363", "13363"),
        ("3647A17636", "717636"),
        ("3651A17936", "117936"),
        ("3651A17997", "117997"),
        ("3720A19354", "19354"),
        ("3747A21041", "721041"),
        ("3751A21437", "121437"),
        ("3752A21439", "221439"),
        ("3949A27243", "927243"),
        ("4002A27500", "227500"),
        ("4345228727", "228727"),
        ("4345228739", "228739"),
        ("4345228746", "228746"),
        ("4450241644", "241644"),
        ("4520250850", "250850"),
        ("4520250860", "250860"),
        ("4532254589", "254589"),
        ("4532254605", "254605"),
        ("4536257121", "257121"),
        ("4536257134", "257134"),
        ("4549261230", "261230"),
        ("4549261237", "261237"),
        ("4549261242", "261242"),
        ("4549261244", "261244"),
        ("4619K01216", "901216"),
        ("4623116529", "116529"),
        ("4624K01604", "401604"),
        ("4635120787", "120787"),
        ("4635120805", "120805"),
        ("4636121860", "121860"),
        ("4641123501", "123501"),
        ("4643124357", "124357"),
        ("4644K02946", "402946"),
        ("4644K02991", "402991"),
        ("4715K05603", "505603"),
        ("4716K05679", "605679"),
        ("4716K05685", "605685"),
        ("4722K06130", "206130"),
        ("4737K07114", "707114"),
        ("4740K10721", "10721"),
        ("4804K53312", "453312"),
        ("4812K54632", "254632"),
        ("4843K33395", "333395"),
        ("4844K59159", "459159"),
        ("4912K61349", "261349"),
        ("4917K61748", "761748"),
        ("4917K61752", "761752"),
        ("4937K63692", "763692"),
        ("4942K64043", "264043"),
        ("5020K67484", "67484"),
        ("5021K67563", "167563"),
        ("5037K70405", "770405"),
        ("5039K70764", "970764"),
        ("5046K71738", "671738"),
        ("5046K71749", "671749"),
        ("5048K71845", "871845"),
        ("5049K72288", "972288"),
        ("5117K75257", "775257"),
        ("5117K75341", "775341"),
        ("5118K75440", "875440"),
        ("5201K41189", "141189"),
        ("5207K82163", "782163"),
        ("5211K83155", "183155"),
        ("5212K83327", "283327"),
        ("5223K85816", "385816"),
        ("5226K50358", "650358"),
        ("5302K41673", "241673"),
        ("5328K44262", "844262"),
        ("5340K46122", "46122"),
        ("5347K47647", "747647"),
        ("5349K48392", "948392"),
        ("5418R48262", "848262"),
        ("5420R48510", "48510"),
        ("5422R48673", "248673"),
        ("5450R50059", "50059"),
        ("5504R50175", "450175"),
        ("5541R50016", "150016"),
        ("5544R50318", "450318"),
        ("5548R50507", "850507"),
        ("5548R50598", "850598"),
        ("5703R51192", "351192"),
        ("5704R51289", "451289"),
        ("5709R51463", "951463"),
        ("5730R50433", "50433"),
        ("5737R50899", "750899"),
        ("5737R50915", "750915"),
        ("5742R51348", "251348"),
        ("5742R51352", "251352"),
        ("5745R51359", "551359"),
        ("5745R51373", "551373"),
        ("5751R52038", "152038"),
        ("5803R40146", "340146"),
        ("5804R40044", "440044"),
        ("5813R40021", "340021"),
        ("5813R40030", "340030"),
        ("5818R40023", "840023"),
        ("5821R50277", "150277"),
        ("5904C01658", "401658"),
        ("5920R40037", "40037"),
        ("5923R40164", "340164"),
        ("5923R40189", "340189"),
        ("5923R40258", "340258"),
        ("5923R40269", "340269"),
        ("5923R40273", "340273"),
        ("6042R40051", "240051"),
        ("6113R40012", "340012"),
        ("6140R40052", "40052"),
        ("6140R40120", "40120"),
        ("6140R40259", "40259"),
        ("ZR20012104", "12104"),
        ("18223034615", "34615"),
        ("8PRM6AZ2EBK", "862"),
        ("8RKF4G9IDXC", "849"),
        ("8RL53NIYFB4", "8534"),
        ("AEHEX8YP6O0", "860"),
        ("AEU34X2NBI8", "3428"),
        ("AEVWYXOEY2O", "2"),
        ("AF0WQJPZSHS", "0"),
        ("AF3ONH2BTHC", "32"),
        ("AFA0JAF1D6O", "16"),
        ("AFB1PAJ162O", "1162"),
        ("AFP2LB8MMM8", "288"),
        ("AFUY1RUPO1S", "11"),
        ("AG0XLFRDTZ4", "4"),
        ("AG6L3MSDUKG", "63"),
        ("AGBV83QBWN4", "834"),
        ("AGL2LHV3XMO", "23"),
        ("AGNV7TGA2O0", "720"),
        ("AGX9Q4B3PQ8", "9438"),
        ("LP019992811", "992811"),
        ("LP020003804", "3804"),
        ("MT300304325", "304325"),
        ("MT301205236", "205236"),
        ("MT310533200", "533200"),
        ("MT310900143", "900143"),
        ("MT311204751", "204751"),
        ("MT311525256", "525256"),
        ("MT311605707", "605707"),
        ("MT312310851", "310851"),
        ("NAP10400016", "400016"),
        ("NAP10400017", "400017"),
        ("P87XQA14C8W", "87148"),
        ("R8598LJM9DS", "85989"),
        ("R8JFPV4PQ0W", "840"),
        ("RT820015201", "15201"),
        ("RT919994505", "994505"),
        ("RT920010203", "10203"),
        ("UX219992013", "992013"),
        ("UX219994206", "994206"),
        ("W1THEGIHDDY", "1"),
        ("W1TOMMLD6VE", "16"),
        ("W1ZSUOS36KO", "136"),
        ("W1ZX8J0O5XK", "1805"),
        ("ZE120024621", "24621"),
        ("ZR200111111", "111111"),
        ("ZR220013820", "13820"),
        ("ZR220013823", "13823"),
        ("ZR220013841", "13841"),
        ("ZR220023809", "23809"),
        ("ZR520021809", "21809"),
        ("ZX199912127", "912127"),
        ("700570E05139", "5139"),
        ("700724B01833", "401833"),
        ("UC2200302010", "302010"),
        ("UC2200302018", "302018"),
        ("UC2200303021", "303021"),
        ("UC2200303025", "303025"),
        ("UC2200439007", "439007"),
        ("ZX 199912136", "912136"),
        ("SC22A9021001E", "21001"),
        ("SC22E1061021G", "61021"),
        ("ZX 4200112203", "112203"),
        ("S/N M00684-24-016", "424016"),
        ("Delta_00031 OEM_066", "31066"),
        ("Delta_00031  OEM_066", "31066"),
        ("Delta_00031 OEM_0665", "310665"),
    )

    for serial, expected in test_data:
        result = build_receiver_no(serial)
        assert result == expected, f"Expected {result!r} to be {expected!r} ..."
