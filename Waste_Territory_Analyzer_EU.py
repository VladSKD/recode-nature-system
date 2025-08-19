import requests
import folium
from sklearn.cluster import KMeans
import numpy as np
import geopandas as gpd
from shapely.geometry import MultiPoint
import time
import requests
from geopy.geocoders import Nominatim
from time import sleep
import os
import json
import time
import requests
import ijson
import csv
import json
import geopandas as gpd


geolocator = Nominatim(user_agent="TrashRouter")

def get_place_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='en')
        if location and "address" in location.raw:
            address = location.raw["address"]
            return address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
    except Exception as e:
        print(f"Reverse geocoding failed at {lat}, {lon}: {e}")
    return None

city_population = {
    "Vienna": 3028289, "Graz": 313848, "Linz": 212538, "Salzburg": 155031, "Innsbruck": 132493, "Brussels": 1211035, "Antwerp": 523248, "Ghent": 263927, "Charleroi": 201816, "Liège": 197355, "Sofia": 1264567, "Plovdiv": 342439, "Varna": 1580177, "Burgas": 202098, "Ruse": 142028, "Zagreb": 807254, "Split": 178102, "Rijeka": 108481, "Osijek": 98789, "Zadar": 75294,
    "Nicosia": 200452, "Limassol": 101000, "Larnaca": 86000, "Prague": 1301132, "Brno": 382405, "Ostrava": 283504, "Plzeň": 176651, "Liberec": 104247, "Aarhus": 349983, "Aalborg": 215986, "Esbjerg": 71568, "Randers": 62329, "Kolding": 60555, "Tallinn": 437619, "Tartu": 96135, "Narva": 55842, "Pärnu": 38364, "Kohtla-Järve": 32690,
    "Helsinki": 658864, "Espoo": 298909, "Tampere": 241201, "Vantaa": 237231, "Turku": 193810, "Paris": 4161000, "Marseille": 870018, "Lyon": 516092, "Toulouse": 493465, "Nice": 343895, "Nantes": 318808, "Strasbourg": 287228, "Montpellier": 295542, "Bordeaux": 257068, "Lille": 233098, "Berlin": 6369491, "Hamburg": 1841179, "Munich": 3471508, "Cologne": 1085664, "Frankfurt": 3753056,
    "Stuttgart": 635911, "Düsseldorf": 617280, "Dortmund": 586000, "Essen": 583109, "Bremen": 567559, "Athens": 664046, "Thessaloniki": 315196, "Patras": 213984, "Heraklion": 140730, "Larissa": 162591, "Budapest": 4000000, "Debrecen": 202214, "Szeged": 161921, "Miskolc": 142279, "Pécs": 139600, "Dublin": 1173179, "Cork": 210000, "Limerick": 95000, "Galway": 80000, "Waterford": 53000,
    "Rome": 2872800, "Milan": 1366180, "Naples": 907000, "Turin": 870952, "Bologna": 390636, "Florence": 382258, "Genoa": 580097, "Verona": 257275, "Venice": 261905, "Bari": 320475, "Riga": 630000, "Daugavpils": 83176, "Liepāja": 69589, "Jelgava": 56172, "Jūrmala": 49757, "Vilnius": 580020, "Kaunas": 293637, "Klaipėda": 147041, "Šiauliai": 100978, "Panevėžys": 91264,
    "Luxembourg City": 128514, "Esch-sur-Alzette": 34964, "Differdange": 25633, "Dudelange": 20127, "Amsterdam": 872757, "Rotterdam": 651446, "The Hague": 549163, "Utrecht": 361924, "Eindhoven": 237180, "Warsaw": 5090658, "Kraków": 779115, "Łódź": 671088, "Wrocław": 3042869, "Poznań": 537454, "Gdańsk": 471525, "Szczecin": 398878, "Bydgoszcz": 345678, "Lublin": 340000, "Katowice": 294510,
    "Lisbon": 506654, "Porto": 231962, "Braga": 181494, "Coimbra": 143396, "Aveiro": 78132, "Bucharest": 1883425, "Cluj-Napoca": 324576, "Timișoara": 319279, "Iași": 290422, "Constanța": 283872, "Bratislava": 437725, "Košice": 238757, "Prešov": 87000, "Žilina": 81200, "Nitra": 78800, "Ljubljana": 295504, "Maribor": 95000, "Celje": 38000, "Kranj": 38000, "Velenje": 25000, "Madrid": 7266126, "Barcelona": 1620343, "Valencia": 791413, "Seville": 688711, "Zaragoza": 1100000,
    "Málaga": 578460, "Murcia": 460349, "Alicante": 337482, "Bilbao": 345141, "Valladolid": 298412, "Stockholm": 975904, "Gothenburg": 588651, "Malmö": 347949, "Uppsala": 233839, "Västerås": 151073, "Paris":2161000,"Marseille":870018,"Lyon":516092,"Nice":343895,"Nantes":318808,"Strasbourg":287228,"Montpellier":295542,"Bordeaux":257068,"Lille":233098,"Rennes":216815,"Reims":183042,"Saint-Étienne":171483,"Toulon":171953,"Le Havre":170147,"Grenoble":158454,"Dijon":156920,"Angers":154508,"Nîmes":150610,"Villeurbanne":149019,"Clermont-Ferrand":142686,"Saint-Denis":112091,"Le Mans":143252,"Aix-en-Provence":143097,"Brest":139602,"Tours":136252,"Limoges":131479,"Amiens":134057,"Metz":116581,"Perpignan":121875,"Besançon":117156,"Orléans":114286,"Boulogne-Billancourt":121334,"Mulhouse":108312,"Rouen":110169,"Caen":106538,"Nancy":104321,"Saint-Paul":104072,"Argenteuil":110388,"Montreuil":109897,"Roubaix":96707,"Tourcoing":96920,"Dunkerque":91680,"Avignon":90708,"Nanterre":95471,"Créteil":91224,"Poitiers":87848,"Versailles":85712,"Colombes":84903,"Asnières-sur-Seine":85150,"Aulnay-sous-Bois":84000,"Rueil-Malmaison":79902,"Antibes":74625,"Saint-Maur-des-Fossés":75341,"Calais":73406,"La Rochelle":75171,"Champigny-sur-Marne":75247,"Saint-Nazaire":69054,"Cannes":73682,"Fort-de-France":85403,"Montauban":60958,"Béziers":76928,"Neuilly-sur-Seine":58388,"Cergy":63650,"Issy-les-Moulineaux":68411,"Levallois-Perret":64800,
    "Madrid": 7266126, "Barcelona": 1020343, "Valencia": 791413, "Seville": 688711, "Zaragoza": 1100000, "Málaga": 578460, "Murcia": 460349, "Palma": 415940, "Las Palmas de Gran Canaria": 381223, "Bilbao": 345141, "Alicante": 337482, "Córdoba": 325708, "Valladolid": 298412, "Vigo": 295364, "Gijón": 271780, "Hospitalet de Llobregat": 264923, "La Coruña": 245711, "Granada": 232770, "Elche": 232517, "Oviedo": 1450567, "Badalona": 218620, "Cartagena": 214802, "Terrassa": 217366, "Jerez de la Frontera": 213105, "Sabadell": 208167, "Móstoles": 206015, "Santa Cruz de Tenerife": 203856, "Pamplona": 201653, "Alcalá de Henares": 195649, "Fuenlabrada": 194708, "Leganés": 188425, "San Sebastián": 186064, "Getafe": 180747, "Burgos": 176418, "Almería": 173762, "Santander": 172539, "Castellón de la Plana": 171728, "Albacete": 171999, "Logroño": 152650, "Huelva": 144258, "Salamanca": 144228, "Marbella": 147633, "Tarragona": 132, "Lleida": 137, "León": 124, "Cádiz": 116, "Badajoz": 150, "Alcorcón": 169, "Jaén": 114,  "Berlin": 6369491, "Hamburg": 1041179, "Munich": 3471508, "Cologne": 1085664, "Frankfurt": 3753056, "Stuttgart": 635911, "Düsseldorf": 617280, "Dortmund": 586000, "Essen": 583109, "Bremen": 567559, "Dresden": 556780, "Leipzig": 593145, "Hanover": 538068, "Nuremberg": 518365, "Duisburg": 498590, "Bochum": 365587, "Wuppertal": 355100, "Bielefeld": 334195, "Bonn": 327258, "Münster": 315293, "Karlsruhe": 313092, "Mannheim": 309721, "Augsburg": 295135, "Wiesbaden": 278342, "Gelsenkirchen": 260654, "Mönchengladbach": 261454, "Braunschweig": 251364, "Chemnitz": 246334, "Kiel": 246794, "Aachen": 247380, "Halle": 239257, "Magdeburg": 237565, "Freiburg": 231195, "Krefeld": 227020, "Lübeck": 216277, "Oberhausen": 210934, "Erfurt": 213699, "Mainz": 217118, "Rostock": 208886, "Kassel": 201585, "Hagen": 188529, "Saarbrücken": 180741, "Hamm": 179397, "Mülheim": 170880, "Herne": 156449, "Ludwigshafen": 172621, "Osnabrück": 164748, "Solingen": 159927, "Leverkusen": 163487, "Oldenburg": 169077, "Neuss": 153234, "Heidelberg": 160355, "Paderborn": 151633, "Darmstadt": 161692, "Regensburg": 153094, "Ingolstadt": 139981, "Würzburg": 127934, "Fürth": 129000, "Wolfsburg": 124151, "Offenbach": 127651, "Ulm": 126790, "Heilbronn": 126592, "Pforzheim": 125542, "Göttingen": 119801, "Bottrop": 117383, "Trier": 113530, "Recklinghausen": 112960, "Reutlingen": 115000, "Bremerhaven": 113643, "Koblenz": 113844,
    "London": 4908081, "Birmingham": 1141816, "Glasgow": 635640, "Liverpool": 498042, "Bristol": 463400, "Manchester": 553230, "Sheffield": 584853, "Leeds": 789194, "Edinburgh": 488050, "Leicester": 355218, "Coventry": 371521, "Kingston upon Hull": 260645, "Bradford": 537173, "Cardiff": 364248, "Belfast": 343542, "Stoke-on-Trent": 255833, "Wolverhampton": 262008, "Nottingham": 331069, "Southampton": 252796, "Reading": 163203, "Derby": 257174, "Dundee": 148270, "Portsmouth": 238137, "Brighton": 290395, "Plymouth": 262100, "Northampton": 225146, "Luton": 214109, "Milton Keynes": 229941, "Norwich": 213166, "Swindon": 222193, "Sunderland": 174286, "Walsall": 214089, "Newcastle upon Tyne": 148917, "Preston": 141314, "Southend-on-Sea": 182463, "Lancaster": 138375, "Huddersfield": 162949, "Exeter": 130428, "Gloucester": 128488, "Bath": 88974, "Oxford": 154326, "Cheltenham": 117154, "Carlisle": 107524, "Canterbury": 55878, "Hereford": 61500,
    "Rome": 2672800, "Milan": 1366180, "Naples": 907000, "Turin": 870952, "Palermo": 663401, "Genoa": 580097, "Bologna": 390636, "Florence": 382258, "Venice": 261905, "Verona": 257275, "Messina": 237041, "Padua": 210440, "Trieste": 204338, "Taranto": 197534, "Brescia": 196480, "Prato": 194590, "Parma": 194417, "Modena": 184293, "Reggio Calabria": 181447, "Reggio Emilia": 172895, "Perugia": 166676, "Ravenna": 159229, "Livorno": 158797, "Cagliari": 154106, "Foggia": 151758, "Rimini": 150590, "Salerno": 133970, "Ferrara": 132009, "Sassari": 130310, "Latina": 126470, "Giugliano in Campania": 123786, "Monza": 123776, "Siracusa": 123244, "Pescara": 121709, "Bergamo": 120718, "Forlì": 118140, "Trento": 117390, "Vicenza": 113639, "Terni": 111425, "Bolzano": 107317, "Novara": 104491, "Piacenza": 102269, "Ancona": 100696, "Udine": 99870, "Arezzo": 98879, "Cesena": 97323, "Lecce": 94872, "Pesaro": 94818, "Barletta": 94168, "Alessandria": 93038, "La Spezia": 93929, "Pistoia": 90449, "Lucca": 88655, "Cremona": 71739, "Brindisi": 86722, "Catanzaro": 89554, "Pisa": 90407, "Trapani": 67695, "Andria": 100000,
    "Warsaw": 5090658, "Kraków": 779115, "Łódź": 671088, "Wrocław": 3042869, "Poznań": 537454, "Gdańsk": 471525, "Szczecin": 398878, "Bydgoszcz": 345678, "Lublin": 340000, "Katowice": 294510, "Białystok": 297554, "Gdynia": 246306, "Częstochowa": 223802, "Radom": 214566, "Toruń": 203158, "Kielce": 196335, "Gliwice": 182156, "Zabrze": 176049, "Olsztyn": 173126, "Bielsko-Biała": 172185, "Rzeszów": 196000, "Ruda Śląska": 137128, "Rybnik": 140000, "Tychy": 130000, "Dąbrowa Górnicza": 120000, "Opole": 128000, "Elbląg": 120000, "Płock": 120000, "Wałbrzych": 110000, "Gorzów Wielkopolski": 124000, "Zielona Góra": 140000, "Tarnów": 110000, "Chorzów": 110000, "Kalisz": 100000,
    "Bucharest": 1083425, "Cluj-Napoca": 324576, "Timișoara": 319279, "Iași": 290422, "Constanța": 283872, "Craiova": 269506, "Brașov": 253200, "Galați": 249432, "Ploiești": 209945, "Oradea": 196367, "Brăila": 180302, "Arad": 159074, "Pitești": 155383, "Sibiu": 147245, "Bacău": 144307, "Târgu Mureș": 134290, "Baia Mare": 123738, "Buzău": 115494, "Satu Mare": 102411, "Râmnicu Vâlcea": 101390, "Sofia": 1264567, "Plovdiv": 342439, "Varna": 1580177, "Burgas": 202098, "Ruse": 142028, "Stara Zagora": 138272, "Pleven": 106954, "Sliven": 91491, "Dobrich": 83584, "Shumen": 75550, "Yambol": 72301, "Pazardzhik": 70107, "Haskovo": 69904, "Blagoevgrad": 69742, "Veliko Tarnovo": 70000,
    "Bratislava": 437725, "Košice": 238757, "Prešov": 87000, "Žilina": 81200, "Nitra": 78800, "Ljubljana": 295504, "Maribor": 95000, "Prague": 1301132, "Brno": 382405, "Ostrava": 283504, "Plzeň": 176651, "Liberec": 104247,
    "Vienna": 3028289, "Graz": 313848, "Linz": 212538, "Salzburg": 155031, "Innsbruck": 132493, "Budapest": 4000000, "Debrecen": 202214, "Szeged": 161921, "Miskolc": 142279, "Pécs": 139600, "Bratislava": 437725, "Košice": 238757, "Prešov": 87000, "Žilina": 81200, "Nitra": 78800, "Ljubljana": 295504, "Maribor": 95000, "Prague": 1301132, "Brno": 382405, "Ostrava": 283504, "Plzeň": 176651, "Liberec": 104247,
    "Amsterdam": 872757, "Rotterdam": 651446, "The Hague": 549163, "Utrecht": 361924, "Eindhoven": 237180, "Brussels": 1211035, "Antwerp": 523248, "Ghent": 263927, "Charleroi": 201816, "Liège": 197355, "Aarhus": 349983, "Aalborg": 215986, "Esbjerg": 71568, "Randers": 62329, "Kolding": 60555,
    "Oslo": 709037, "Bergen": 283929, "Trondheim": 205163, "Stavanger": 480000, "Kristiansand": 95000, "Stockholm": 975904, "Gothenburg": 588651, "Malmö": 347949, "Uppsala": 233839, "Västerås": 151073, "Helsinki": 658864, "Espoo": 298909, "Tampere": 241201, "Vantaa": 237231, "Turku": 193810,
    "Vilnius": 580020, "Kaunas": 293637, "Klaipėda": 147041, "Šiauliai": 100978, "Panevėžys": 91264, "Tallinn": 437619, "Tartu": 96135, "Riga": 630000, "Daugavpils": 83176, "Liepāja": 69589,
    "Metz": 116581, "Dalbok Izvor": 1500, "Saint-Joseph": 38000, "Cilaos": 5500, "Byszewy": 3200, "Castelo de Paiva": 11000, "Kristinehamns kommun": 24371, "Ormesson-sur-Marne": 8000, "Budrio": 17189, "Brno": 382405, "Merville": 9500, "Hamina": 22189, "Rotterdam": 651446, "Alfeld (Leine)": 18000, "Meyreuil": 9000, "Buenavista del Norte": 200500, "Madrid": 7266126, "Aquilonia": 1900, "North Devon": 35000,
    "Trondheim": 205163, "Liffré": 11000, "Munich": 3471508, "Sângeorz-Băi": 12000, "Lyon": 516092, "Stavanger": 480000, "Skjervøy": 2800, "Upplands Väsby": 2810000, "Wierzchląd": 6700, "Kourou": 25000, "Stuttgart": 635911, "Municipal Unit of Levidi": 5800, "Campo Ligure": 3000, "Umeå kommun": 89000, "Gronau": 48000, "Skierbieszów": 2700, "City of London": 3982000, "Rasnov": 16000, "Budapest": 4000000,
    "Pouillon": 1200, "Randers": 62000, "Oborovo Bistransko": 2500, "Garkalnes pagasts": 2000000, "Etzelkofen": 700, "Rome": 2872800, "Saint-Vincent-Cramesnil": 400, "Zell": 13000, "Zlatník": 1800, "Rabenau": 10000, "Nittedal": 24000, "(12.26, -69.26)": 0, "Alella": 10000, "Orzesze": 6010000, "Herbault": 1000, "Fortuna": 13000, "La Puebla del Río": 15000,
    "Mamoudzou": 42000, "Villeneuve-d'Ascq": 62000, "Alhandra, São João dos Montes e Calhandriz": 13000, "Helsinki": 658864, "Vallensbæk Municipality": 16000, "Glasgow": 635000, "Ylitornio": 4500, "Lødingen": 2300, "Clermont-Ferrand": 142000, "Junta de Traslaloma": 800, "Łapalice": 600, "Plomari": 7500, "Kamvounia Municipal Unit": 4500, "Slobozia": 43000, "Påryd": 1200,
    "Ponta Delgada": 280000, "Ua Pou": 2300, "Bolton": 194189, "Szafranki": 1000, "Gavardo": 12000, "Wrocław": 3042869, "Feldkirchen an der Donau": 5300,
    "Couëron": 15000, "Saint-Robert": 1200, "Vonges": 1000, "Paroy-sur-Tholon": 700, "Murianette": 2800, "Caurel": 900, "Jarzé Villages": 4000, "Narbonne": 54000, "Guerbigny": 600, "Roquefort-le": 800,
    "Geleen": 32000, "Wamel": 5000, "Reichshof": 21000, "Hohn": 3500, "Neu Wulmstorf": 20000, "Voluntari": 47000, "Dăbâca": 2300, "Dăeni": 2000, "Grumo Appula": 1500000, "Castelfranco Veneto": 2500000, "Castelfiorentino": 22000, "Cesate": 9000,
    "Meløy": 7400, "Gjemnes": 2800, "Partille kommun": 37000, "Jelšava": 6000, "Malá Mača": 2400, "Grad Skradin": 3000, "Nowodwór": 1800, "Trzebownisko": 10000,
    "Laitila": 7500, "Jyväskylä": 143000, "Lazkao": 10000, "Alaquàs": 22000, "Kottes-Purk": 1500, "Niederhasli": 9000, "Thal": 8000, "Saint Paul's Bay": 13000, "Savigné": 2000, "Balatonmagyaród": 500, "Kodersdorf Bahnhof": 800, "Manoppello": 7000,
    "Reignier-Ésery": 9000, "Larvik": 47000, "Bergen": 280000, "Ardales": 2500, "Kienheim": 1500, "Oviedo": 1450567, "Berlin": 6369491, "Preveza": 13000, "Loriol-sur-Drôme": 4500, "Dundee": 148000, "Leogang": 1500, "Embūtes pagasts": 750000, "Ludwigshafen am Rhein": 172000, "Kosoř": 1200,
    "Municipal Unit of Nea Filadelfeia": 20000, "Novi Iskar": 3500000, "Santana": 110000, "Saint-Quentin-de-Baron": 2200, "Villesse / Vilès": 2500, "Zaragoza": 1100000, "Osby kommun": 750000, "Cáceres": 96000, "Himberg": 11000, "South Varanki": 1000,
    "Kiekrz": 3000, "Las Palmas de Gran Canaria": 380000, "Hofors kommun": 12000, "Glauchau": 25000, "Plancher-Bas": 800, "Philippeville": 12000, "Langenfeld (Rheinland)": 60000, "Amsterdam": 872000, "Warsaw": 5090000, "Huélago": 2000, "Újszentmargita": 2500, "Campo Lameiro": 1800,
    "Asiūklė": 1500, "Diepholz": 13000, "Vatnestrøm": 500, "Ylihärmä": 1000, "Brenner - Brennero": 2000, "Paterno Calabro": 3000, "Jokkmokks kommun": 5000, "Sønderborg": 28000, "Bellaguarda": 400, "Rimatara": 100800, "Steinkjer": 23000, "Καρδία": 3000,
    "Forssa": 16000, "Unterbleichen": 1000, "Tylice": 1500, "Rușii-Mănăstioara": 700, "Merrey-sur-Arce": 600, "Turin": 870000, "Saint-André-de-Briouze": 1200, "Afragola": 6040000,
    "Linköpings kommun": 780000, "Le Langon": 1400, "Palmia": 800, "Senja": 7000, "Plavilla": 300, "Sântămărie": 500, "Villamor de los Escuderos": 400, "Stepenitztal": 6000,
    "Ringkøbing-Skjern Municipality": 56000, "Toulon-sur-Arroux": 2000, "Melbach": 700, "Volda": 10500, "Montignargues": 450, "Vysoká nad Labem": 5000, "Porsanger": 3500,
    "Nowa Wieś Ostródzka": 1200, "Montierchaume": 1000, "Åsele kommun": 3000, "Tolentino": 1318000, "Siikalatva": 6200, "Saint-Lézer": 600, "Máriakéménd": 1300,
    "Debelets": 3500, "Gräfenberg": 7500, "Romenay": 1200, "Peize": 7300, "Galgauskas pagasts": 2000, "Igny-Comblizy": 3000, "Mošovce": 3800, "Voiceștii din Vale": 1500,
    "Klosterrode": 900, "Sagonne": 500, "Karwin": 60000, "Meise": 19000, "Rhodes": 35000, "Nestelbach bei Graz": 1500, "Le Faou": 1500, "Gerdžiai": 400, "Hesmond": 250,
    "Kisdombegyház": 2000, "Nanterre": 96000, "Borgo Pace": 2500700, "Darnétal": 12000, "Saint-Félix-de-Lunel": 700, "Craintilleux": 650, "Lindforst": 300, "Francavilla Fontana": 2536000,
    "Prétot-Sainte-Suzanne": 900, "Göslow": 1100, "Poindimié": 3500, "Derby": 255000, "Sechereșa": 400, "Święciny": 1200, "Pointe-à-Pitre": 150000, "Åre kommun": 11000,
    "Agullana": 903, "Nuku Hiva": 200025, "Debovo": 439, "Hamnvik": 200000, "Mary": 167027, "Municipality of Agioi Anargyroi-Kamatero": 54000, "Keskastel": 1541, "Nechanice": 2508, "Vieux-Fort": 4574, "Ede": 124214, "Imola": 69332,
    "Mogoșești": 3725, "Karlstadt": 14720, "Velles": 1117, "Kunágota": 2342, "Vulliens": 361, "Mereto di Capitolo": 780, "Póvoa de Santa Iria e Forte da Casa": 38332, "Simiane-Collongue": 5900, "Saterland - Seelterlound": 13238, "Rosnoën": 1072, "Kangasala": 32290, "Fundeni - Dobroești": 27619, "Semoine": 357, "A Chan": 450, "Roye": 5930, "Vefsn": 133074, "Pudasjärvi": 7691, "Lelekovice": 1821, "Großenohe": 234, 
    "Ljubljana": 295504, "Krakow": 800653, "Oviedo": 1450567, "Kongsberg": 27000, "Savonlinna": 32787, "Vienna": 3028289, "Graz": 313848, "Linz": 212538, "Salzburg": 155031, "Innsbruck": 132493, "Kalmar kommun": 271600, "Tervuren": 22291, "Dilsen-Stokkem": 20872, "Neenstetten": 843, "Couëron": 21534, "Kauhava": 15805, "Kristinehamns kommun": 23972, "Arvidsjaurs kommun": 6497, "Brissac-Loire-Aubance": 6613, "Moncalieri": 56000, "Montlouis-sur-Loire": 10710, "Griesheim": 26467, "Vernouillet": 10171,
    "Cassina de' Pecchi": 13500, "Sandbostel": 850, "Gioia del Colle": 27000, "Badajoz": 150000, "Osera de Ebro": 400, "Grans sameby": 200, "Karlsfeld": 21000, "Beaufort": 2200, "Conques-en-Rouergue": 1600, "Orzechowo": 1000, "Kristinehamns kommun": 24000, "Quaix-en-Chartreuse": 900, "Heřmanovice": 300, "Ljubljana": 295000, "Montlouis-sur-Loire": 11000, "Dolný Harmanec": 200, "Buenavista del Norte": 200500, "Krakow": 800000, "Charmoy": 400, "Kauhava": 16000, "Kerviai": 200, "Gelsted": 3000, "Verdal": 15000, "Vernouillet": 10000, "Himberg": 8000, "Kielnarowa": 1600, "Dilsen-Stokkem": 20000, "Griesheim": 27000, "Brissac-Loire-Aubance": 5000, "Quesnoy-sur-Deûle": 7000, "Borki": 2500, "Râșca": 8000, "Moncalieri": 57000, "Neenstetten": 850, "Montrond-les-Bains": 5000, "San Martino di Lupari": 13000, "Municipal Unit of Vytina": 2000, "Středokluky": 1200, "Dunaharaszti": 21000, "Hengelo": 81000, "Péron": 2500, "Kongsberg": 27000, "Zarzec Ulański": 700, "Calzada de Don Diego": 500, "Montois-la-Montagne": 5700, "Spenge": 15000, "Salo": 53000, "Savigné": 1300, "Marcilly-en-Villette": 2500,
    "Roquefort-les-Pins": 7000, "Savonlinna": 33000, "Saint-Romain-de-Colbosc": 5800, "Oviedo": 1450567, "Guerlédan": 2500, "Kalmar kommun": 271000, "Kazashka Reka": 200, "Vigeois": 1100, "Raková": 3000, "Tervuren": 22000, "Behren-Lübchin": 800, "Penne": 1200, "Pitulați": 400, "Simo": 3100, "Vettelschoß": 3500, "Geibonys": 100, "Arló": 3600, "Kammersrohr": 60, "Weißenbach am Lech": 300, "Arvidsjaurs kommun": 6300, "Rurka": 150, "Aubière": 10000, "Couëron": 21000, "Općina Sveti Ilija": 5300,
    "Salerno":132600,"Olomouc Region":632000,"Finistère":916000,"North Ostrobothnia":200000,"Troms":165000,"Västerbotten County":270000,"Bologna":390000,"Seine-Maritime":123900,"Sächsische Schweiz-Osterzgebirge":250000,"Varaždin County":175000,"South Holland":2000000,"Cher":310000,"Upper Savoy":285000,"Novi Iskar":3500000,"Västernorrland County":245000,"Elektrėnų seniūnija":21000,"Bihor":575000,"Södermanland County":290000,"Roma Capitale":2873000,"Kalmar County":245000,"Møre og Romsdal":265000,"Marne":570000,"Haute-Garonne":135000,"District of Revúca":30000,"Bezirk Graz-Umgebung":130000,"Limburg":5750000,"Maine-et-Loire":820000,"Southwest Finland":1300000,"Baranya":360000,"Metropolitan France":670000,"Finnmark":75000,"Landkreis Günzburg":130000,"Ain":650000,"Comarca de València":800000,"District of Turčianske Teplice":25000,"Baia":100000,"Arcadia Regional Unit":86000,"Arad":430000,"Rogaland":480000,"Lesbos Regional Unit":86000,"Ortenaukreis":425000,"Kreis Gütersloh":360000,"Moselle":750000,"Cluj":720000,"Martinique":375000,"Maritime Alps":150000,"Côtes-d'Armor":600000,
    "Łódź Voivodeship":2400000,"Warwickshire":560000,"Pontevedra":945000,"Castile and León":900000,"Gołdap County":26000,"Stade":115000,"Börde":110000,"Jaama District":18000,"Vâlcea":380000,"Sulęcin County":35000,"Udine":100000,"Vienne":430000,"Bezirk Bruck an der Leitha":100000,"Bezirk Innsbruck-Land":170000,"Vorpommern-Rügen":230000,"Castile-La Mancha":735000,"Parma":200000,"Ilm-Kreis":110000,"Dundee City":150000,"Constanța":320000,"Bezirk Urfahr-Umgebung":130000,"District Zurich":2500000,"Landkreis Cham":133000,"Zaragoza":1100000,"Subcarpathian Voivodeship":1200000,"Aude":370000,
    "Oise":830000,"Silesian Voivodeship":1700000,"North Province":250000,"Réunion":860000,"Community of Madrid":7270000,"Landkreis Cham":130000,"Uppsala County":380000,"Brașov":650000,"Ain":650000,"Innlandet":370000,"Landkreis Darmstadt-Dieburg":290000,"Province of Padua":950000,"Santana":110000,"Maine-et-Loire":820000,"Harju County":600000,"Naples":960000,"Lesbos Regional Unit":86000,"Pas-de-Calais":145000,"England":6000000,"Haute-Garonne":135000,"French Guiana":300000,"Rogaland":480000,"Halle-Vilvoorde":120000,"Nordland":240000,"Krasnystaw County":130000,"Lisbon":550000,"Hradec Králové Region":550000,"Central Denmark Region":1252000,"Varese":900000,"Territoire-de-Belfort":144000,"Spodnji Duplek":20000,"Budapest":4000000,"Capital Region of Denmark":4150000,"Aetolia-Acarnania Regional Unit":200000,"Overijssel":3720000,"Świecie County":120000,"Hamburg":180000,"Kielce County":200000,"South Ostrobothnia":470000,"Drôme":520000,"Loire-Atlantique":140000,"Thessaloniki Regional Unit":110000,"Mayotte":300000,"Arcadia Regional Unit":86000,"Las Palmas de Gran Canaria":380000,
    "North Ostrobothnia":200000,"Bezirk Bregenz":200000,"Trøndelag":470000,"Plāņu pagasts":5000,"Sächsische Schweiz-Osterzgebirge":250000,"el Baix Segura / La Vega Baja":400000,"Gironde":160000,"Bragança":150000,"Pyrénées-Atlantiques":700000,"Sierra de Cádiz":250000,"Loiret":670000,"Hunedoara":400000,"Upper Savoy":285000,"South Moravian Region":120000,"Ełk County":100000,"Szabolcs-Szatmár-Bereg":900000,"Bezirk Mödling":100000,"Cuneo":600000,"Macerata":320000,"French Polynesia":280000,"Gelderland":5600000,"Seine-Maritime":123900,"Râșca":10000,"Mansfeld-Südharz":250000,"Northern Region":300000,"Nièvre":210000,"Brindisi":400000,"District Zurich":2500000,"Vallès Oriental":450000,"Lower Silesian Voivodeship":1900000,"South Savo":700000,"Roma Capitale":287300,"Glasgow City":630000,"Côte-d'Or":530000,"Finistère":916000,"Aube":310000,"Møre og Romsdal":265000,"Telemark":170000,"Regional Unit of North Athens":150000,"Bezirk Innsbruck-Land":170000,"Udine":100000,"Upper Austria":1700000,"Florence":380000,"Troms":165000,"Corrèze":240000,"Castile and León":900000,"Berlin":6369491,
    "Aleksandrijos seniūnija":20000,"Var":110000,"District of Revúca":30000,"Varna":1580177,"Łańcut County":130000,"West Pomeranian Voivodeship":3300000,"Coimbra":140000,"Kreis Steinfurt":300000,"Västerbotten County":270000,"North Holland":280000,"Cosenza":700000,"Sofia":130000,"Bas-Rhin":110000,"Ponta Delgada":280000,"Landkreis Rhön-Grabfeld":100000,"Split-Dalmatia County":450000,"Stockholm County":230000,"Koszalin County":150000,"Alb-Donau-Kreis":190000,
    "Zala": 290000, "Isère": 1250000, "Moselle": 1040000, "Lubartów County": 100000, "Lot-et-Garonne": 330000, "Kreis Mettmann": 285000, "Landkreis Rostock": 220000, "Gúdar-Javalambre": 10000, "Dundee City": 148000, "Akershus": 640000, "Västra Götaland County": 170000, "Vienne": 435000, "Central Denmark Region": 1252000, "Kalmar County": 240000, "Verona": 260000, "Masovian Voivodeship": 540000, "Landkreis Forchheim": 130000, "Nord": 600000, "Brăila": 320000, "Plovdiv": 680000, "Tabeirós - Terra de Montes": 100000, "Central Finland": 275000, "Olt": 350000, "Aveyron": 280000, "Torino": 2200000, "Békés": 400000, "Southwest Finland": 1300000, "Landkreis München": 1000060, "Maramureș": 500000, "Indre-et-Loire": 600000, "Amtei Bucheggberg-Wasseramt": 20000, "Comarca de la Vega de Granada": 100000, "Wieliczka County": 130000, "Yonne": 340000, "Castile and León": 900000, "Central Bohemia": 1300000, "District of Banská Bystrica": 300000, "Loire": 750000, "District of Galanta": 100000, "Orne": 300000, "Côtes-d'Armor": 600000, "Yvelines": 1400000, "Drenthe": 1250000,
    "Moravian-Silesian Region": 1200000, "Castile-La Mancha": 735000, "Landkreis Berchtesgadener Land": 100000, "Aegean Region": 3000000, "Blekinge County": 150000, "Indre": 230000, "Landkreis Hildesheim": 300000, "Asturias": 1000000, "Norrbotten County": 250000, "Skadanščina": 10000, "Larisa Regional Unit": 150000, "Elektrėnų seniūnija": 20000, "Troms": 165000, "Region Zealand": 850000, "Vendée": 700000, "Maaseik": 40000, "Avellino": 430000, "Mureș": 700000, "Doubs": 540000, "Ilfov": 400000, "Vestland": 640000, "Maritime Alps": 300000, "Pescara": 320000, "Buenavista del Norte": 200500, "South Holland": 2000000, "Dalarna County": 280000, "Puy-de-Dôme": 650000, "Agder": 300000, "Bouches-du-Rhône": 2000000, "Philippeville": 10000, "Pyrénées-Atlantiques": 700000, "Lucca": 380000, "Västernorrland County": 250000, "Leicestershire": 1100000, "Seine-Maritime": 1239000, "Jaama District": 50000, "District of Prešov": 800000, "South Tyrol": 530000, "Regionalverband Saarbrücken": 150000, "Zaragoza": 1100000, "Krosno Odrzańskie County": 100000, "Iași": 320000, "Landkreis Böblingen": 250000,
    "Olaines pagasts": 10000, "Bezirk Klagenfurt-Land": 100000, "Greater Poland Voivodeship": 3500000, "Bezirk Krems": 30000, "French Polynesia": 280000, "Alessandria": 420000, "Zgierz County": 200000, "Garrigues": 10000, "Landkreis Osterholz": 100000, "Bari": 330000, "Rhein-Sieg-Kreis": 600000, "Finnmark": 74000, "Kanta-Häme": 700000, "Soz County": 30000, "Southwest": 500000, "Erzgebirgskreis": 800000, "Ile-de-France": 4120000, "Martinique": 400000, "Brescia": 130000, "Somme": 570000, "Lazdukalna pagasts": 5000, "Évora": 150000, "Ille-et-Vilaine": 100000, "Baranya": 1000000, "Nordborg": 20000, "Dordogne": 400000, "Kreis Paderborn": 300000, "Opole County": 800000, "Uusimaa": 3750000, "Porto": 2300000, "Gard": 750000,
    "Metropolitan France": 67000000, "Silesian Voivodeship": 1700000, "Koné": 180000, "French Guiana": 300000, "Réunion": 860000, "Hällefors kommun": 7000, "French Polynesia": 280000, "Extremadura": 1100000, "Lombardy": 4000000, "Pleven": 240000, "Lääne-Harju vald": 11000, "Grand Est": 1550000, "Occitania": 2500000, "Lower Saxony": 1500000, "Apulia": 400000, "Normandy": 1000000, "Buenavista del Norte": 2005000, "Auvergne-Rhône-Alpes": 1200000, "Masovian Voivodeship": 540000, "Bavaria": 4700000, "North Holland": 290000, "Ørsta": 10000, "Scotland": 5500000, "Målselv": 8000, "Pays de la Loire": 1025000, "Epirus and Western Macedonia": 500000, "Region of Trnava": 1550000, "West Pomeranian Voivodeship": 3300000, "Castile-La Mancha": 735000, "Vorarlberg": 400000, "Brittany": 1200000, "Region of Prešov": 1200000, "Skjetten": 20000, "Attica": 3500000, "Capital Region of Denmark": 4150000, "Piobbico": 1000, "Poiana Stoichii": 2000, "Greater Poland Voivodeship": 3500000, "Trentino – Alto Adige/Südtirol": 1100000, "North Savo": 180000, "Nouvelle-Aquitaine": 700000, "Penafiel": 60000, "Brussels-Capital": 120000,
    "Bourgogne – Franche-Comté": 900000, "England": 6000000, "North Rhine-Westphalia": 6000000, "Saxony": 3240000, "Skatval": 3000, "Rosersberg": 5000, "Carinthia": 960000, "Valencian Community": 500000, "Alhandra, São João dos Montes e Calhandriz": 10000, "Călan": 20000, "North Ostrobothnia": 200000, "Solothurn": 2500000, "Mayotte": 300000, "South Ostrobothnia": 470000, "Hesse": 610000, "Central Denmark Region": 1252000, "Podlaskie Voivodeship": 1990000, "Macedonia and Thrace": 2550000, "Centre-Val de Loire": 6200000, "Andalusia": 8400000, "Budapest": 4000000, "Drenthe": 1250000, "Älmhults kommun": 20000, "Castile and León": 900000, "Ponta Delgada": 280000, "Plovdiv": 680000, "Provence-Alpes-Côte d'Azur": 6400000, "Alta": 200000, "Lublin Voivodeship": 1300000, "Vaiņodes pagasts": 1500, "Catalonia": 830000, "Hauts-de-France": 2750000, "Gelderland": 5600000, "Vevelstad": 1000, "Kvinesdal": 6000, "Veneto": 2500000, "Calabria": 1900000, "Lesser Poland Voivodeship": 3300000, "Abruzzo": 2300000, "Piedmont": 4300000, "Varna": 1580177, "Lejasciema pagasts": 2000,
    "Lower Silesian Voivodeship": 1900000, "Kuyavian-Pomeranian Voivodeship": 2100000, "South Great Plain": 1000000, "Lerum": 28000, "Bucharest": 1900000, "Lower Austria": 570000, "Jokkmokks kommun": 5000, "Schleswig-Holstein": 4800000, "Koper / Capodistria": 25000, "Pomeranian Voivodeship": 230000, "Santana": 110000, "Părău": 1000, "Asturias": 100000, "Overijssel": 3720000,
    "Community of Madrid":7270000,"Apulia":4000000,"England":6000000,"Tuscany":3700000,"South Savo":700000,"Baden-Württemberg":5500000,"Normandy":1000000,"Larvik":47000,"Campania":580000,"Central Moravia":2410000,"Brittany":1200000,"North Ostrobothnia":200000,"Kvæfjord":2900,"Emilia-Romagna":2450000,"Saxony":3240000,"South Holland":2000000,"Centre-Val de Loire":6200000,"Auvergne-Rhône-Alpes":1200000,"Sofia-City":130000,"Vilnius County":810000,"Vingåkers kommun":9000,"Lazio":6700000,"Nybro kommun":19000,"Surnadal":6500,"Grand Est":1550000,"Occitania":2500000,"Region of Banská Bystrica":660000,"Styria":1200000,"Limburg":5750000,"Pays de la Loire":1025000,"Southwest Finland":1300000,"Southern Transdanubia":1700000,"Metropolitan France":700000,"Bavaria":4700000,"Valencian Community":500000,"Region of Žilina":690000,"Peloponnese, Western Greece and the Ionian":1100000,"Stavanger":480000,"Aegean":300000,"North Rhine-Westphalia":600000,"Martinique":375000,"Provence-Alpes-Côte d'Azur":6400000,"Łódź Voivodeship":2400000,"Galicia":2700000,"Castile and León":900000,
    "Warmian-Masurian Voivodeship":1100000,"Lower Saxony":1500000,"Saxony-Anhalt":2200000,"Leningrad Oblast":1700000,"Lubusz Voivodeship":1000000,"Friuli – Venezia Giulia":1200000,"Nouvelle-Aquitaine":700000,"Lower Austria":570000,"Tyrol":750000,"Mecklenburg-Vorpommern":1600000,"Castile-La Mancha":735000,"Thuringia":4510000,"Scotland":550000,"Upper Austria":1700000,"Zurich":2500000,"Aragon":130000,"Subcarpathian Voivodeship":1200000,"Bodø":51000,"Lombardy":4000000,"Hauts-de-France":2750000,"Andalusia":840000,"Piedmont":2700000,"Region of Crete":60000,"Kanta-Häme":700000,"Birkenes":5000,"Berlin":6369491,"Lublin Voivodeship":1300000,"French Polynesia":280000,"Central Bohemia":130000,"Epirus and Western Macedonia":500000,"Lower Silesian Voivodeship":290000,"Bourgogne – Franche-Comté":900000,"Castro Verde":677000,"Lapland":180000,
    "Cyprus":1276500, "Corsica":355528, "Ireland":5380300, "Sardinia":1650000, "Sicily":2785338, "Balearic Islands":940332, "Iceland":383726, "Malta": 574346,
    "Antequera": 41000, "Autonomous Community of the Basque Country": 2220000, "Belpasso": 1909000, "Bodensee (SG)": 2208000, "Brasov": 110000, "Buciumeni": 2500, "Cassano delle Murge": 14000, "Chiari": 19000, "City of Varaždin": 47000, "Corleone": 1611000, "Elektrėnai": 13000, "Falu kommun": 850000, "Fribourg": 2500000, "Harsewinkel": 25000, "Holy Cross Voivodeship": 1250000, "Iveland": 1300, "Izvoarele": 5000, "Kvænangen": 1200, "Landvetter": 7800, "Larbert": 4500, "Lebesby": 1300, "Ljungsbro": 9500, "Līgo pagasts": 1100, "Malå sameby": 3100, "Mariestads kommun": 240000, "Mettmann": 39000, "Mihail Kogălniceanu": 6500, "Montcada i Reixac": 33000, "Mustvee vald": 4700, "Naxxar": 630000, "Nesseby": 950, "Nesselwängle": 430, "North Karelia": 162000, "Northeast": 900000, "Northwest": 760000, "Notodden": 13000, "Nuneaton and Bedworth": 130000, "Opole Voivodeship": 980000, "Općina Pučišća": 1600, "Oria": 12000, "Orta di Atella": 28000, "Picioru Lupului": 1900, "Region of Košice": 800000, "Region of Trenčín": 600000, "Rhineland-Palatinate": 410000, "Ronneby kommun": 29000, "Saarland": 1580000, "Skaun": 8500, "South Karelia": 130000, "Southeast": 870000, "St. Marein bei Graz": 2700, "Stange": 20500, "Steigen": 205000, "Sub Pădure": 600, "Ulmeni": 7200, "Uppsala kommun": 230000, "Vestby": 18000, "Vila Franca de Xira": 1400000, "Vilvoorde": 45000, "Vâlcelele": 3700, "Vărșand": 1800, "Wels": 63000, "Ådals-Liden District": 1500, "Övertorneå kommun": 4400,
    "Askersunds kommun": 11100, "Atrå": 600, "Autonomous Republic of Crimea": 1900000, "Baldovinești": 3500, "Brenguļu pagasts": 1300, "Cazalla de la Sierra": 4900, "Cherkasy Oblast": 2170000, "Chernihiv Oblast": 990000, "Chernivtsi Oblast": 900000, "City of Zagreb": 770000, "Dobroteasa": 700, "Donetsk Oblast": 4200000, "Evenes": 1400, "Grimstad": 24000, "Habo kommun": 12000, "Hainaut": 1340000, "Hedemora kommun": 15000, "Kharkiv Oblast": 2600000, "Khmelnytskyi Oblast": 2560000, "Kirovohrad Oblast": 900000, "Klaipeda County": 313000, "Kyiv": 2960000, "Kåfjord": 2100, "Kåhög": 950, "Leipheim": 7000, "Liguria": 2000000, "Loures": 2900000, "Luhansk Oblast": 1800000, "Lukovo": 2500, "Lviv Oblast": 2200000, "Lünen": 88000, "Marchtrenk": 15000, "Marghita": 18000, "Moravia-Silesia": 1200000, "Mykolaiv Oblast": 1920000, "North Hungary": 1000000, "Northwich": 20000, "Odesa Oblast": 2400000, "Olofströms kommun": 13000, "Oriv": 800, "Poltava Oblast": 2200000, "Region of Nitra": 690000, "Ridderkerk": 47000, "Sagna": 1700, "San Severino Marche": 13000, "Sandefjord": 64000, "Sant Vicent del Raspeig / San Vicente del Raspeig": 58000, "Saronno": 40000, "Skodborg": 1800, "Ternopil Oblast": 1430000, "Tromsø": 77000, "Tunari": 6700, "Valestrandsfossen": 2600, "Valle de Valdebezana": 1200, "Vidigueira": 6000, "Vinnytsia Oblast": 2000000, "Vișeu de Sus": 15000, "Võru vald": 14000, "Vălioara": 900, "Western Transdanubia": 1000000, "Zakopane": 27000, "Zaporizhia Oblast": 3800000, "okres Vyškov": 92000, "Łańcut": 18000, "Șilea": 2800,
    "Capital City of Prague": 2794435, "Central Hungary": 1310000, "Monforte de Lemos": 18560, "Verdalsøra": 8838,                 
    "Afumați": 2730480, "Anundsjö District": 3533, "Balsfjord": 200627, "Beiarn": 1062, "Bercioiu": 489, "Bodbyn": 200000, "Bodens kommun": 28048, "Carugate": 1000740, "Chirileni": 804700, "Criuleni": 670800, "Gaigalavas pagasts": 757, "Golineasa": 23, "Grünenplan": 2421, "Guadeloupe": 378561, "Heby kommun": 14345, "Ikornnes": 840, "Kauguru pagasts": 1326, "Kinn": 17179,
    "Kloten": 21652, "Levanger": 470344, "Lohusuu alevik": 322, "Marche": 1484427, "Melhus": 17560, "Muncelu Mic": 700, "Mykolaiv Urban Hromada": 1625700, "Măstăcani": 5144, "Navarre": 1322155, "Netezi": 4275, "Neustift im Stubaital": 5006, "Općina Selca": 564100, "Peuerbach": 3443, "Poličnik": 4569, "Priego de Córdoba": 14222, "Pruszcz Gdański": 580244, "Pustodol": 1000, "Rivne Oblast": 2034500, "Rättviks kommun": 10661, "Sant Josep de sa Talaia": 30480, "Santău": 3032, "Satakunta": 212653, "Skien": 55924, "Sollentuna kommun": 73000, "St. Gallen": 75000, "Sønderborg Municipality": 75000, "Săcel": 1310, "Tana": 2028, "Ulvik": 1046, "Vadsø": 5807, "Valle de Losa": 224, "Vågan": 10168, "Wallis": 351000, "Weißenhorn": 12274, "Ålvund": 300, "Šamorín": 13887, "Republic of Crimea": 1934000,
    "A Estrada": 2710880, "Alboraia / Alboraya": 3240741, "Bonnybridge": 5480070, "Bord": 3127800, "Brand-Erbisdorf": 391450, "Burgenland": 294436, "Coșnița": 1599960, "Diemen": 5313340, "Dos Hermanas": 2930430, "Drangedal": 330000, "East Lindsey": 5611500, "Foltești": 910256, "Guadix": 2260000, "Ivano-Frankivsk Oblast": 1661109, "Ixelles - Elsene": 2800000, "Jonsered": 1145000, "Junsele District": 372000, "Kelstrup Strand": 1805000, "Kyiv Oblast": 5680000, "Lindesnes": 290000, "Logatec": 1700000, "Marijampole County": 1500000, "Metropolitan Borough of Solihull": 1400000, "Montgat": 250000, "Mérida": 1100000, "Nordre Follo": 1600000, "Općina Stubičke Toplice": 2250000, "Orihuela": 3400000, "Paredes": 4200000, "Parvomay": 1850000, "Pedrógão Grande": 20000, "Pranciškonys": 1200000, "Ramnes": 400000, "Rindal": 130000, "Ringsaker": 370000, "Rõuge vald": 850000, "Rătești": 900000, "Strážov": 900000, "Stânca": 3800000, "Sæbø": 1300000, "Toplița": 2100000, "Tornaľa": 600000, "Velbert": 6000000, "Verguleasa": 530000, "Votlo": 440000, "Vuonnabahta - Varangerbotn": 200000, "Zemunik Gornji": 400000, "Álora": 3000000, "Överkalix kommun": 250000, "Ireland_cluster_0": 7000000,  "Iceland_cluster_0": 404123,
}







# Словник з ISO кодами країн Європи
europe_iso_codes = {
    "France": "FR",
    "Germany": "DE",
    "Austria": "AT",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Estonia": "EE",
    "Finland": "FI",
    "Greece": "GR",
    "Hungary": "HU",
    "Iceland": "IS",
    "Ireland": "IE",
    "Italy": "IT",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Malta": "MT",
    "Netherlands": "NL",
    "Norway": "NO",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Spain": "ES",
    "Sweden": "SE",
    "Switzerland": "CH",
    "United Kingdom": "GB",
    "Ukraine": "UA",
    "Moldova": "MD"
}



# збережння, глянемо, чи все нормік
# 2. Підрахунок потенціалу сміття за об'єктами (умовні коефіцієнти)
# Тонни сміття на тиждень для типових об’єктів
WASTE_COEFF = {
    "school": 0.3,
    "hospital": 2.1,
    "clinic": 1.0,
    "hotel": 1.5,
    "dormitory": 0.7,
    "kindergarten": 0.2,
    "vocational_school": 0.4,
    "college": 0.5,
    "cinema": 0.6,
    "restaurant": 0.8,
    "cafe": 0.3,
    "canteen": 0.7,
    "retail_store": 0.4,
    "grocery_store": 0.6,
    "marketplace": 1.2,
    "train_station": 1.5,
    "university": 1.0
}

# Середній обсяг сміття на людину (тонн/тиждень)
WASTE_PER_PERSON_PER_WEEK = 0.0098



def fetch_osm_data_light_europe(sleep_sec=8, cache_file="data/europe_osm_light.json"):
    if os.path.exists(cache_file):
        print(f"✅ Завантаження легких даних з кешу: {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            all_elements = json.load(f)
        print(f"Загальна кількість об'єктів у легкому файлі: {len(all_elements)}")
        return all_elements

    all_elements = []
    total_countries = len(europe_iso_codes)
    for idx, (country, iso) in enumerate(europe_iso_codes.items(), start=1):
        print(f"[{idx}/{total_countries}] Завантаження легких даних для {country} ({iso})...")
        query = f"""
        [out:json][timeout:180];
        relation["ISO3166-1"="{iso}"][admin_level=2];
        map_to_area->.searchArea;
        (
          node["amenity"="school"](area.searchArea);
          node["amenity"="hospital"](area.searchArea);
        );
        out body;
        """
        try:
            response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
            response.raise_for_status()
            data = response.json()
            elements = data.get("elements", [])
            print(f"  -> Отримано об'єктів: {len(elements)}")
            all_elements.extend(elements)
        except Exception as e:
            print(f"  !!! Помилка для {country}: {e}")
        print(f"Очікуємо {sleep_sec} секунд перед наступним запитом...\n")
        time.sleep(sleep_sec)

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(all_elements, f, ensure_ascii=False, indent=2)
    print(f"Загальна кількість отриманих об'єктів у легкому файлі по Європі: {len(all_elements)}")
    return all_elements




amenities = list(WASTE_COEFF.keys())
amenities_query_parts = [f'node["amenity"="{amenity}"](area.searchArea);' for amenity in amenities]
amenities_query = "\n          ".join(amenities_query_parts)

def fetch_osm_data_for_subregion(osm_id):
    
    query = f"""
    [out:json][timeout:180];
    relation({osm_id});
    map_to_area->.searchArea;
    (
      {amenities_query}
    );
    out body;
    """
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
    response.raise_for_status()
    data = response.json()
    return data.get("elements", [])

def get_country_relation_id(iso):
    #
    if iso == "FR":
        return 2202162  #  id Франції
    
    query = f"""
    [out:json][timeout:25];
    relation["ISO3166-1"="{iso}"][admin_level=2];
    out ids;
    """
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
    response.raise_for_status()
    data = response.json()
    elements = data.get("elements", [])
    if elements:
        return elements[0]["id"]
    return None

def get_subregions(country_relation_id, admin_level=4):
    area_id = 3600000000 + country_relation_id
    query = f"""
    [out:json][timeout:180];
    area({area_id})->.searchArea;
    relation(area.searchArea)["admin_level"="{admin_level}"];
    out ids tags;
    """
    response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
    response.raise_for_status()
    data = response.json()
    subregions = []
    for el in data.get("elements", []):
        if el.get("type") == "relation":
            subregions.append({
                "osm_id": el["id"],
                "name": el.get("tags", {}).get("name", f"region_{el['id']}")
            })
    return subregions


import math

def save_elements_in_chunks(elements, base_filename="data/europe_osm_full", max_mb=23):
    os.makedirs(os.path.dirname(base_filename), exist_ok=True)

    max_bytes = max_mb * 1024 * 1024  
    chunk = []
    total_chunks = 0
    current_size = 0

    def get_file_name(idx):
        return f"{base_filename}_{idx:02d}.json"

    for el in elements:
        el_json = json.dumps(el, ensure_ascii=False)
        el_size = len(el_json.encode("utf-8"))
        if current_size + el_size > max_bytes:
            total_chunks += 1
            with open(get_file_name(total_chunks), "w", encoding="utf-8") as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            chunk = []
            current_size = 0
        chunk.append(el)
        current_size += el_size


    if chunk:
        total_chunks += 1
        with open(get_file_name(total_chunks), "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)

    print(f"🔹 Успішно збережено в {total_chunks} файлів по ~{max_mb} МБ.")



def fetch_osm_data_all_europe_full(sleep_sec=8, cache_file="data/europe_osm_full.json"):
    if os.path.exists(cache_file):
        print(f"✅ Завантаження детальних даних з кешу: {cache_file}")
        with open(cache_file, "r", encoding="utf-8") as f:
            all_elements = json.load(f)
        print(f"Загальна кількість об'єктів у великому файлі: {len(all_elements)}")
        return all_elements

    all_elements = []
    total_countries = len(europe_iso_codes)

    for idx, (country, iso) in enumerate(europe_iso_codes.items(), start=1):
        print(f"[{idx}/{total_countries}] Обробка країни {country} ({iso})...")

        country_rel_id = get_country_relation_id(iso)
        if not country_rel_id:
            print(f"  Не вдалося знайти relation id країни {country}")
            continue


        subregions = get_subregions(country_rel_id, admin_level=4)
        print(f"  Знайдено субрегіонів: {len(subregions)}")

        if len(subregions) == 0:
            print(f"  Субрегіонів не знайдено, завантажуємо дані по всій країні...")
            query = f"""
            [out:json][timeout:180];
            relation({country_rel_id});
            map_to_area->.searchArea;
            (
              {amenities_query}
            );
            out body;
            """
            try:
                response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
                response.raise_for_status()
                data = response.json()
                elements = data.get("elements", [])
                print(f"  Отримано об'єктів: {len(elements)}")
                all_elements.extend(elements)
            except Exception as e:
                print(f"  !!! Помилка для {country}: {e}")
            print(f"Очікуємо {sleep_sec} секунд перед наступним запитом...\n")
            time.sleep(sleep_sec)
        else:
            for i, subr in enumerate(subregions, 1):
                print(f"    [{i}/{len(subregions)}] Завантаження даних для {subr['name']} (OSM id: {subr['osm_id']})")
                try:
                    elements = fetch_osm_data_for_subregion(subr['osm_id'])
                    print(f"      Отримано об'єктів: {len(elements)}")
                    all_elements.extend(elements)
                except Exception as e:
                    print(f"      !!! Помилка завантаження для {subr['name']}: {e}")
                print(f"    Очікуємо {sleep_sec} секунд...")
                time.sleep(sleep_sec)

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    save_elements_in_chunks(all_elements, base_filename="data/europe_osm_full", max_mb=23)

    print(f"Загальна кількість отриманих об'єктів по Європі: {len(all_elements)}")
    return all_elements


def load_all_chunks(base_filename="data/europe_osm_full"):
    files = sorted([f for f in os.listdir("data") if f.startswith("europe_osm_full_") and f.endswith(".json")])
    total_files = len(files)
    all_elements = []

    print(f"📥 Завантаження {total_files} частин...")

    for idx, f_name in enumerate(files, start=1):
        with open(os.path.join("data", f_name), "r", encoding="utf-8") as f:
            data = json.load(f)
            all_elements.extend(data)

        percent = int((idx / total_files) * 100)
        print(f"  [{idx}/{total_files}] {f_name} ➤ {percent}% готово")

    print(f"\n✅ Комбінування завершено. Загальна кількість об'єктів: {len(all_elements)}")
    return all_elements


def combine_chunks_to_full_file(base_filename="data/europe_osm_full", full_file="data/europe_osm_full.json"):
    print("🗂️ Об’єднуємо всі частинки в один повний файл...")
    elements = load_all_chunks(base_filename)
    with open(full_file, "w", encoding="utf-8") as f:
        json.dump(elements, f, ensure_ascii=False, indent=2)
    print(f"✅ Повний файл створено: {full_file}")
    return elements





def calculate_total_waste(region_data):
    
    total_waste = 0.0

    # 1. Сміття від населення
    total_waste += region_data.get("population", 0) * WASTE_PER_PERSON_PER_WEEK

    # 2. Сміття від об’єктів
    objects = region_data.get("objects", {})
    for obj_type, count in objects.items():
        coeff = WASTE_COEFF.get(obj_type, 0)
        total_waste += count * coeff

    return total_waste  



# 3. Обробка даних, формування списку об'єктів з координатами та вагами
def process_elements(elements):
    points = []
    for el in elements:
        if "tags" not in el:
            continue
        amenity = el["tags"].get("amenity")
        if amenity not in WASTE_COEFF:
            continue
        lat = el.get("lat")
        lon = el.get("lon")
        if lat is None or lon is None:
            continue
        waste = WASTE_COEFF[amenity]
        points.append({
            "type": amenity,
            "lat": lat,
            "lon": lon,
            "waste": waste,
        })
    return points


island_bounds = {
    "Corsica": (41.3, 43.1, 8.5, 9.7),
    "Sardinia": (38.8, 41.4, 8.0, 9.9),
    "Sicily": (36.3, 38.4, 12.3, 15.7),
    "Ireland": (51.4, 55.4, -10.5, -5.5),
    "Cyprus": (34.4, 35.7, 32.2, 34.0),
    "Palma": (39.2, 39.9, 2.4, 3.5),
    "Iceland": (63.2, 66.6, -24.5, -13.0),
    "Malta": (35.8, 36.1, 14.2, 14.6)
}

def is_in_bounds(p, bounds):
    lat, lon = p["lat"], p["lon"]
    min_lat, max_lat, min_lon, max_lon = bounds
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

def split_points_islands_mainland(points):
    island_points = {}
    mainland_points = []
    for p in points:
        matched = False
        for island, bounds in island_bounds.items():
            if is_in_bounds(p, bounds):
                island_points.setdefault(island, []).append(p)
                matched = True
                break
        if not matched:
            mainland_points.append(p)
    return island_points, mainland_points


geolocator = Nominatim(user_agent="TrashRouter")




# це якщо в нас нище, ніж тавн (праивльне, надіюсь) (кажись ні)
def get_place_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='en')
        if location and "address" in location.raw:
            address = location.raw["address"]

            place = address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
            if place:
                is_lower_level = bool(address.get("village") or address.get("municipality"))

                if is_lower_level:
                    admin_above = address.get("state") or address.get("region")
                    if admin_above:
                        return admin_above
                return place
    except Exception as e:
        print(f"Reverse geocoding failed at {lat}, {lon}: {e}")
    return None




unmatched_regions = set()




def get_population_for_place(place_name):
    if not place_name:
        return 0
    key = place_name.strip().lower()
    for city, pop in city_population.items():
        if city.lower() == key:
            return pop
    print(f"{place_name} не знайдено у словнику. Додаємо 0.")
    unmatched_regions.add(place_name)
    return 0


def get_population_for_cluster(region_name, cluster_id, lat, lon):
    place_name = get_place_name(lat, lon)
    if place_name:
        pop = get_population_for_place(place_name)
        if pop:
            print(f"    Населення {place_name} знайдено у словнику: {pop}")
            return place_name, pop
        else:
            print(f"    {place_name} не знайдено у словнику. Додаємо 0.")
            return place_name, 0
    else:
        print("    Не вдалося визначити назву місця")
        if region_name in ["Ireland", "Iceland"]:
            key = f"{region_name}_cluster_{cluster_id}"
            pop = city_population.get(key, 0)
            if pop:
                print(f"    Для {key} населення взято зі словника: {pop}")
            else:
                print(f"    Для {key} населення у словнику відсутнє, ставимо 0")
            return "Невідомо", pop
        else:
            return "Невідомо", 0


# 4. Кластеризація за координатами з урахуванням ваги сміття 
def cluster_points(points, n_clusters=10):
    if not points:
        return {}

    coords = np.array([[p["lat"], p["lon"]] for p in points])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(coords)

    clusters = {}
    for i in range(n_clusters):
        clusters[i] = {
            "points": [],
            "total_waste": 0,
            "center": None,
        }

    for p, label in zip(points, labels):
        clusters[label]["points"].append(p)
        clusters[label]["total_waste"] += p["waste"]

    # Обчислення вагового центру з урахуванням "waste"
    for i in range(n_clusters):
        cluster = clusters[i]
        if not cluster["points"]:
            continue
        weighted_lat = sum(p["lat"] * p["waste"] for p in cluster["points"])
        weighted_lon = sum(p["lon"] * p["waste"] for p in cluster["points"])
        total_waste = cluster["total_waste"]
        cluster["center"] = (weighted_lat / total_waste, weighted_lon / total_waste)
    return clusters




# 5. Створення полігонів (кордонів) регіонів
def create_cluster_polygons(clusters):
    polygons = {}
    for cluster_id, cluster in clusters.items():
        points = [(p["lon"], p["lat"]) for p in cluster["points"]]  
        if len(points) < 3:
            center_lon, center_lat = cluster["center"][1], cluster["center"][0]
            point = gpd.GeoSeries([gpd.points_from_xy([center_lon], [center_lat])[0]])
            poly = point.buffer(0.05).iloc[0]
            polygons[cluster_id] = poly
        else:
            multipoint = MultiPoint(points)
            try:
                poly = multipoint.convex_hull
            except Exception:
                poly = multipoint.envelope
            polygons[cluster_id] = poly
    return polygons





from geopy.distance import geodesic

def assign_full_points_to_clusters(full_points, clusters):

    for region, cluster_dict in clusters.items():
        for cluster_id in cluster_dict:
            cluster_dict[cluster_id]['full_points'] = []
            cluster_dict[cluster_id]['total_waste_objects'] = 0

    for p in full_points:
        p_lat, p_lon = p['lat'], p['lon']
        closest_region = None
        closest_cluster_id = None
        min_dist = float('inf')

        for region, cluster_dict in clusters.items():
            for cluster_id, cluster_data in cluster_dict.items():
                center = cluster_data.get('center')
                if center is None:
                    continue
                center_lat, center_lon = center
                dist = geodesic((p_lat, p_lon), (center_lat, center_lon)).meters
                if dist < min_dist:
                    min_dist = dist
                    closest_region = region
                    closest_cluster_id = cluster_id
        
        if closest_region is not None and closest_cluster_id is not None:
            clusters[closest_region][closest_cluster_id]['full_points'].append(p)
            clusters[closest_region][closest_cluster_id]['total_waste_objects'] += p.get('waste', 0)

    return clusters

import ijson

def load_full_points_streaming(file_path, log_every=100_000):
    full_points = []
    print(f"▶️ Починаємо поступове завантаження з {file_path}...\n")

    with open(file_path, 'r', encoding='utf-8') as f:
        objects = ijson.items(f, 'item')  
        for i, obj in enumerate(objects, 1):
            full_points.append(obj) 

            if i % log_every == 0:
                print(f"🔄 Завантажено {i:,} об'єктів...")

    print(f"\n✅ Завершено. Всього завантажено: {len(full_points):,} об'єктів.\n")
    return full_points



from shapely.geometry import Point

def update_clusters_with_full_data(clusters, full_points, log_every=100_000):
    from time import time
    from shapely.geometry import Point

    start_time = time()
    total_points = len(full_points)

    flat_cluster_map = {}
    for group in clusters.values():
        for cluster_id, cluster in group.items():
            cluster.setdefault('points', [])
            cluster.setdefault('total_waste_objects', 0)
            flat_cluster_map[cluster_id] = cluster

    # Створюємо полігони
    polygons = create_cluster_polygons(flat_cluster_map)

    for i, p in enumerate(full_points, 1):
        point = Point(p["lon"], p["lat"])
        waste = p.get("waste", 1)

        for cluster_id, polygon in polygons.items():
            if polygon.contains(point):
                flat_cluster_map[cluster_id]['total_waste_objects'] += waste
                flat_cluster_map[cluster_id]['points'].append(p)
                break

        if i % log_every == 0 or i == total_points:
            percent = (i / total_points) * 100
            elapsed = time() - start_time
            print(f"🔄 Оброблено {i:,} з {total_points:,} точок ({percent:.2f}%). Час: {elapsed:.1f} сек")

    print(f"✅ Завершено. Загальний час: {time() - start_time:.1f} сек")
    return clusters



# 6. Візуалізація на карті
def visualize_clusters(cluster_groups, cluster_populations):
    import folium
    import geopandas as gpd
    from collections import defaultdict

    def get_color_by_waste(weight):
        if weight <= 5000:
            return "lightblue"
        elif weight <= 12000:
            return "blue"
        elif weight <= 20000:
            return "green"
        elif weight <= 30000:
            return "orange"
        elif weight <= 45000:
            return "red"
        elif weight <= 65000:
            return "darkred"
        else:
            return "black"

    m = folium.Map(location=[52.0, 19.0], zoom_start=5)

    color_counts = defaultdict(int)  

    for region, clusters in cluster_groups.items():
        polygons = create_cluster_polygons(clusters)
        for cluster_id, cluster in clusters.items():
            place_name, population = cluster_populations[region][cluster_id]
            human_waste = population * WASTE_PER_PERSON_PER_WEEK
            real_total = cluster.get('total_waste_objects', cluster['total_waste']) + human_waste

            color = get_color_by_waste(real_total)
            color_counts[color] += 1

            poly = polygons[cluster_id]
            geojson = gpd.GeoSeries([poly]).__geo_interface__

            folium.GeoJson(
                geojson,
                style_function=lambda f, color=color: {
                    'fillColor': color,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.3,
                },
                name=f"{region} {cluster_id}"
            ).add_to(m)

            if cluster["center"]:
                popup_text = f"{region} {cluster_id}: ≈{real_total:.1f} т/тиж"
                folium.Marker(
                    location=cluster["center"],
                    icon=folium.Icon(color=color, icon="trash", prefix='fa'),
                    popup=popup_text
                ).add_to(m)

    print("Кількість кластерів за кольорами:")
    for color, count in color_counts.items():
        print(f"{color}: {count}")

    return m







def print_waste_area_and_cluster_distribution(cluster_groups, cluster_populations, WASTE_PER_PERSON_PER_WEEK):
    
    bins = [
        (0, 1000),
        (1001, 10000),
        (10001, 30000),
        (30001, 70000),
        (70001, 150000),
        (150001, float('inf')),
    ]
    bin_counts = {f"{low}-{high if high != float('inf') else '+'}": 0 for (low, high) in bins}

    for region, clusters in cluster_groups.items():
        print(f"Регіон: {region}")

        polygons = create_cluster_polygons(clusters)

        for cluster_id, cluster in clusters.items():
            place_name, population = cluster_populations[region][cluster_id]
            human_waste = population * WASTE_PER_PERSON_PER_WEEK
            waste_objects = cluster.get('total_waste_objects', cluster.get('total_waste', 0))
            real_total = waste_objects + human_waste

            poly = polygons.get(cluster_id)
            area_km2 = None
            if poly:
                gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[poly])
                gdf = gdf.to_crs(epsg=3857)
                area_km2 = gdf.geometry.area.iloc[0] / 1_000_000

            area_str = f"{area_km2:.2f} км²" if area_km2 is not None else "Площа невідома"

            print(f"  Кластер {cluster_id}: ≈{real_total:.1f} т/тиж, Площа: {area_str}")

            for low, high in bins:
                if low <= real_total <= high:
                    key = f"{low}-{high if high != float('inf') else '+'}"
                    bin_counts[key] += 1
                    break

        print()

    print("Розподіл кластерів за ваговими діапазонами (тонн/тиж):")
    for interval, count in bin_counts.items():
        label = interval if '+' not in interval else "150000+"
        print(f"  {label}: {count} кластерів")

def save_cluster_data_to_csv(cluster_groups, cluster_populations, WASTE_PER_PERSON_PER_WEEK, filename="clusters_data.csv"):
    data_rows = []

    for region, clusters in cluster_groups.items():
        polygons = create_cluster_polygons(clusters)

        for cluster_id, cluster in clusters.items():
            place_name, population = cluster_populations[region][cluster_id]
            human_waste = population * WASTE_PER_PERSON_PER_WEEK
            waste_objects = cluster.get('total_waste_objects', cluster.get('total_waste', 0))
            total_waste = human_waste + waste_objects

            center = cluster.get("center", (None, None))
            center_lat, center_lon = center if center else (None, None)

            poly = polygons.get(cluster_id)
            area_km2 = None
            polygon_coords = None
            if poly:
                gdf = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[poly])
                gdf = gdf.to_crs(epsg=3857)
                area_km2 = gdf.geometry.area.iloc[0] / 1_000_000  # м² -> км²

                if hasattr(poly, 'exterior'):
                    polygon_coords = list(poly.exterior.coords)
                else:
                    polygon_coords = None

            data_rows.append({
                "cluster_id": cluster_id,
                "region": region,
                "center_lat": center_lat,
                "center_lon": center_lon,
                "area_km2": area_km2 if area_km2 is not None else "",
                "waste_tonnes_week": total_waste,
                "waste_from_population": human_waste,
                "waste_from_objects": waste_objects,
                "polygon": json.dumps(polygon_coords) if polygon_coords else "",
            })

    # Запис у CSV
    fieldnames = ["cluster_id", "region", "center_lat", "center_lon", "area_km2",
                  "waste_tonnes_week", "waste_from_population", "waste_from_objects", "polygon"]

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)

    print(f"Дані кластерів збережено у файл: {filename}")

def main():
    light_file = "data/europe_osm_light.json"
    full_file = "data/europe_osm_full.json"

    if os.path.exists(light_file):
        print(f"Завантаження легких даних з {light_file}...")
        with open(light_file, "r", encoding="utf-8") as f:
            light_elements = json.load(f)
    else:
        print(f"Файл {light_file} не знайдено. Створюємо легкі дані...")
        light_elements = fetch_osm_data_light_europe(cache_file=light_file)

    print("Обробка легких даних (створення точок)...")
    light_points = process_elements(light_elements)
    island_points_light, mainland_points_light = split_points_islands_mainland(light_points)
    print(f"Знайдено точок на материку: {len(mainland_points_light)}")
    print(f"Знайдено островів: {len(island_points_light)}")

    avg_cluster_capacity = 100  

    total_waste_light = sum(p["waste"] for p in mainland_points_light)
    mainland_n = max(1, round(total_waste_light / avg_cluster_capacity))
    print(f"Загальна вага сміття на материку (легкі дані): {total_waste_light:.1f} тонн")
    print(f"Кількість кластерів для материку: {mainland_n}")

    clusters = {}
    print("Створення кластерів для материку...")
    clusters["Mainland"] = cluster_points(mainland_points_light, mainland_n)

    for island, pts in island_points_light.items():
        if pts:
            island_total = sum(p["waste"] for p in pts)
            island_n = max(1, round(island_total / avg_cluster_capacity))
            print(f"Створення {island_n} кластерів для острова {island} ")
            clusters[island] = cluster_points(pts, island_n)

    # --- Отримання населення по центрах кластерів (тільки по легким даним) ---
    from time import sleep


    cluster_populations = {}
    for region_name, cluster_dict in clusters.items():
        cluster_populations[region_name] = []
        print(f"\nОтримання населення для регіону: {region_name}")
        for cluster_id, cluster_data in cluster_dict.items():
            center = cluster_data["center"]
            if not center:
                cluster_populations[region_name].append(("Невідомо", 0))
                continue
            lat, lon = center
            place_name = get_place_name(lat, lon)
            print(f"  Кластер {cluster_id}: координати {center}, пошук населеного пункту...")
            sleep(0.5)
            if place_name:
                pop = get_population_for_place(place_name)
                if pop:
                    print(f"    Населення {place_name} знайдено у словнику: {pop}")
                    cluster_populations[region_name].append((place_name, pop))
                else:
                    print(f"    {place_name} не знайдено у словнику. Додаємо 0.")
                    cluster_populations[region_name].append((place_name, 0))
            else:
                print("    Не вдалося визначити назву місця")
                if region_name in ["Ireland", "Iceland"]:
                    key = f"{region_name}_cluster_{cluster_id}"
                    pop = city_population.get(key, 0)
                    if pop:
                        print(f"    Для {key} населення зі словника: {pop}")
                    else:
                        print(f"    Для {key} населення не знайдено, ставимо 0")
                    cluster_populations[region_name].append(("Невідомо", pop))
                else:
                    cluster_populations[region_name].append(("Невідомо", 0))




    # 2. Завантаження повних даних (для точного підрахунку сміття)
    full_file = "data/europe_osm_full.json"
    base_filename = "data/europe_osm_full"

    if os.path.exists(full_file):
        print(f"Завантаження повних даних з {full_file}...")
        # Якщо потрібен список елементів, можна відкрити великий файл
        with open(full_file, "r", encoding="utf-8") as f:
            elements = json.load(f)
    else:
        # Якщо великого файлу немає, перевіримо наявність частинок
        chunk_files = [f for f in os.listdir("data") if f.startswith(os.path.basename(base_filename) + "_") and f.endswith(".json")]
        if chunk_files:
            # Якщо є частинки — об’єднуємо їх у великий файл
            elements = combine_chunks_to_full_file(base_filename, full_file)
        else:
            # Якщо немає ні великого файлу, ні частинок — завантажуємо нові дані
            print(f"Файл {full_file} не знайдено. Створюємо повні дані...")
            elements = fetch_osm_data_all_europe_full(cache_file=full_file)


    full_points = load_full_points_streaming(full_file, log_every=100_000)

    print(f"Завантажено {len(full_points):,} точок з усіма полями.")

    island_points_full, mainland_points_full = split_points_islands_mainland(full_points)


    clusters = update_clusters_with_full_data(clusters, full_points, log_every=100_000)

    

    # Підрахунок уточненої ваги сміття з повних даних
    total_clusters = sum(len(c) for c in clusters.values())
    count = 0
    total_waste_from_objects = 0

    for cluster_dict in clusters.values():
        for cluster in cluster_dict.values():
            total_waste_from_objects += cluster.get('total_waste_objects', 0)
            count += 1
            
            # Вивід прогресу кожні 10 кластерів
            if count % 10 == 0 or count == total_clusters:
                percent = (count / total_clusters) * 100
                print(f"Оброблено {count} з {total_clusters} кластерів ({percent:.2f}%) — поточна вага сміття: {total_waste_from_objects:.2f} тонн")

    print_waste_area_and_cluster_distribution(clusters, cluster_populations, WASTE_PER_PERSON_PER_WEEK)

 


    total_population = sum(pop for _, pop in cluster_populations["Mainland"])
    total_population += 40000000
    total_waste_from_people = total_population * WASTE_PER_PERSON_PER_WEEK
    total_waste = total_waste_from_objects + total_waste_from_people

    print(f"\n🔥 Уточнена оцінка сміття по материку:")
    print(f"👥 Населення: {total_population:,}")
    print(f"♻️ Від людей: {total_waste_from_people:.1f} тонн/тижд")
    print(f"🏭 Від об'єктів: {total_waste_from_objects:.1f} тонн/тижд")
    print(f"📦 ВСЬОГО: {total_waste:.1f} тонн/тижд")
    
    print("\n📍 Розподіл сміття по кластерах:")






    # --- Візуалізація кластерів з повними даними ---
    print("Візуалізація кластерів ...")
    m = visualize_clusters(clusters, cluster_populations)
    m.save("europe_trash_router.html")
    print("Карта збережена у europe_trash_router.html")


    if unmatched_regions:
        print("\n🔍 Регіони без знайденого населення у словнику:")
        for region in sorted(unmatched_regions):
            print(f" - {region}")
    else:
        print("\n✅ Всі регіони знайдено у словнику населення.")

    save_cluster_data_to_csv(clusters, cluster_populations, WASTE_PER_PERSON_PER_WEEK, filename="clusters_data.csv")



if __name__ == "__main__":
    main()




