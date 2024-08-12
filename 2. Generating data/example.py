obj1 = {
        "url": "https://gcn.joshw.info/x/X-Men%20Legends%20II%20-%20Rise%20of%20Apocalypse%20(2005-09-20)(Raven)(Vicarious%20Visions)(Activision)[GC].7z",
        "name": "X-Men Legends II - Rise of Apocalypse (2005-09-20)(Raven)(Vicarious Visions)(Activision)[GC].7z",
        "size": 293,
        "date": "2018-12-08 20:15",
        "system": "gcn"
    }
    
obj2 = {
        "url": "https://gcn.joshw.info/l/Legend%20of%20Zelda,%20The%20-%20The%20Wind%20Waker%20[Zelda%20no%20Densetsu%20-%20Kaze%20no%20Takuto]%20(2002-12-13)(Nintendo%20EAD)(Nintendo)[GC].7z",
        "name": "Legend of Zelda, The - The Wind Waker [Zelda no Densetsu - Kaze no Takuto] (2002-12-13)(Nintendo EAD)(Nintendo)[GC].7z",
        "size": 140,
        "date": "2013-08-13 12:40",
        "system": "gcn"
    }
    
obj3 = {
        "url": "https://gcn.joshw.info/l/Luigi's%20Mansion%20[Luigi%20Mansion]%20(2001-09-14)(Nintendo%20EAD)(Nintendo)[GC][unplayable].7z",
        "name": "Luigi's Mansion [Luigi Mansion] (2001-09-14)(Nintendo EAD)(Nintendo)[GC][unplayable].7z",
        "size": 16,
        "date": "2023-08-25 15:50",
        "system": "gcn"
    }
    
obj4 = {
        "url": "https://gcn.joshw.info/l/Legend%20of%20Zelda,%20The%20-%20The%20Wind%20Waker%20[Zelda%20no%20Densetsu%20-%20Kaze%20no%20Takuto]%20(2002-12-13)(Nintendo%20EAD)(Nintendo)[GC].7z",
        "name": "Legend of Zelda, The - The Wind Waker [Zelda no Densetsu - Kaze no Takuto] (2002-12-13)(Nintendo EAD)(Nintendo)[GC].7z",
        "size": 140,
        "date": "2013-08-13 12:40",
        "system": "gcn"
    }


def dict_to_tuple(d):
    return tuple(sorted(d.items()))

def tuple_to_dict(t):
    return dict(t)

objects = [obj1, obj2, obj3, obj4]

# Convert to tuples and create a set
object_set = set(dict_to_tuple(obj) for obj in objects)
unique_objects = [tuple_to_dict(t) for t in object_set]
# To view the set
print(unique_objects)
