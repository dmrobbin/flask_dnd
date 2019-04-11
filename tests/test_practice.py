def format_dict(dict):
    del dict["id"]
    del dict["JOB"]
    dict[1] = dict.pop("LEVEL_1")
    dict[2] = dict.pop("LEVEL_2")
    dict[3] = dict.pop("LEVEL_3")
    dict[4] = dict.pop("LEVEL_4")
    dict[5] = dict.pop("LEVEL_5")
    dict[6] = dict.pop("LEVEL_6")
    dict[7] = dict.pop("LEVEL_7")
    dict[8] = dict.pop("LEVEL_8")
    dict[9] = dict.pop("LEVEL_9")
    dict[10] = dict.pop("LEVEL_10")
    dict[11] = dict.pop("LEVEL_11")
    dict[12] = dict.pop("LEVEL_12")
    dict[13] = dict.pop("LEVEL_13")
    dict[14] = dict.pop("LEVEL_14")
    dict[15] = dict.pop("LEVEL_15")
    dict[16] = dict.pop("LEVEL_16")
    dict[17] = dict.pop("LEVEL_17")
    dict[18] = dict.pop("LEVEL_18")
    dict[19] = dict.pop("LEVEL_19")
    dict[20] = dict.pop("LEVEL_20")

def test_it_does_not_blow_up():
    assert 1 == 1

def test_format_dict():
	sample_dict ={"id":13, "JOB":'jobless', "LEVEL_1":1, "LEVEL_2":1,"LEVEL_3":1, "LEVEL_4":1,"LEVEL_5":1, "LEVEL_6":1,"LEVEL_7":1, "LEVEL_8":1,
	"LEVEL_9":1, "LEVEL_10":1,"LEVEL_11":1, "LEVEL_12":1,"LEVEL_13":1, "LEVEL_14":1,"LEVEL_15":1, "LEVEL_16":1,"LEVEL_17":1, "LEVEL_18":1,"LEVEL_19":1, "LEVEL_20":1}

	ideal_dict={}
	for x in range(20):
		ideal_dict[x+1]=1

	format_dict(sample_dict)
	assert sample_dict == ideal_dict