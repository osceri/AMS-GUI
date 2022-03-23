import re

with open("monitor.ui", "r") as m:
    lines = m.readlines()

def indexer(index):
    if index == 0:
        return ""
    else:
        return f"_{index+1}"

def scfi(index):
    return (2*(index // 21) + ((index % 21) // 11) + 1, ((index % 21) % 11) + 1)
def stfi(index):
    return ((index // 5) + 1, (index % 5) + 1)

entries = [ "segment_temp_node" + indexer(index) for index in range(65) ]

hr_ = 0
vr_ = 0
pv_r = 0

for index, line in enumerate(lines):
    if "segment_temperature_horizontal" in line:
        hr_ += 1
        pv_ = 0
    if "segment_temperature_vertical_p" in line:
        vr_ += 1


    ve_s = re.search(r'name="(\w*)"', line)
    if ve_s:
        result = ve_s.group()[6:-1]
        if result in entries:
            p = entries.index(result)
            row = re.search(r'column="(\d*)"', lines[index-1]).group()[8:-1]
            
            s, t = stfi(index)


            rpl = pv_
            pv_ += 1

            rpl = str(rpl)
            print(rpl, row)
            lines[index-1] = lines[index-1].replace(f'column="{row}"', f'column="{rpl}"')
            continue

with open("monitorp2.ui", "w") as m:
    m.write("".join(lines))
