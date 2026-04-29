from pathlib import Path
from xml.sax.saxutils import escape
import re

base = Path(r'D:/01_code/600000_skill/skills/图标创意设计-app-icon-designer/assets')
template_path = base / '_sample_UI.vdx'
out_path = base / 'app-icon-designer-swimlane.vdx'

template = template_path.read_text(encoding='utf-8')

start_token = '<Shapes>'
end_token = '</Shapes>'
start = template.index(start_token) + len(start_token)
end = template.index(end_token)
prefix = template[:start]
suffix = template[end:]

content = prefix + suffix
content = re.sub(r"<PrintLandscape>.*?</PrintLandscape>", "<PrintLandscape>1</PrintLandscape>", content, count=1)
content = re.sub(r"ViewCenterX='[^']+' ViewCenterY='[^']+'", "ViewCenterX='8' ViewCenterY='6.5'", content, count=2)
content = re.sub(r"<PageWidth Unit='IN_F'>.*?</PageWidth>", "<PageWidth Unit='IN_F'>16</PageWidth>", content, count=1)
content = re.sub(r"<PageHeight Unit='IN_F'>.*?</PageHeight>", "<PageHeight Unit='IN_F'>13</PageHeight>", content, count=1)
prefix = content[:content.index(start_token) + len(start_token)]
suffix = content[content.index(end_token):]

shape_id = 1
shapes_meta = {}

def esc_text(text: str) -> str:
    return escape(text).replace('\n', '&#10;')

def char_block(size_pt: int) -> str:
    return f"""
<Char IX='0'>
<Font F='Inh'>0</Font>
<Color F='Inh'>0</Color>
<Style F='Inh'>0</Style>
<Case F='Inh'>0</Case>
<Pos F='Inh'>0</Pos>
<FontScale F='Inh'>1</FontScale>
<Locale F='Inh'>0</Locale>
<Size Unit='PT'>{size_pt}</Size>
<DblUnderline F='Inh'>0</DblUnderline>
<Overline F='Inh'>0</Overline>
<Strikethru F='Inh'>0</Strikethru>
<Perpendicular F='Inh'>0</Perpendicular>
<Letterspace F='Inh'>0</Letterspace>
<ColorTrans F='Inh'>0</ColorTrans>
</Char>"""

def line_block(color='#404040', weight='0.01875', end_arrow='0', begin_arrow='0', rounding='0.02') -> str:
    return f"""
<Line>
<LineWeight>{weight}</LineWeight>
<LineColor>{color}</LineColor>
<LinePattern>1</LinePattern>
<Rounding>{rounding}</Rounding>
<EndArrowSize>2</EndArrowSize>
<BeginArrow>{begin_arrow}</BeginArrow>
<EndArrow>{end_arrow}</EndArrow>
<LineCap>0</LineCap>
<BeginArrowSize>2</BeginArrowSize>
<LineColorTrans>0</LineColorTrans>
</Line>"""

def fill_block(fg='#FFFFFF', bg='#FFFFFF', pattern='1', fg_trans='0', bg_trans='0') -> str:
    return f"""
<Fill>
<FillForegnd>{fg}</FillForegnd>
<FillBkgnd>{bg}</FillBkgnd>
<FillPattern>{pattern}</FillPattern>
<ShdwForegnd>0</ShdwForegnd>
<ShdwBkgnd>1</ShdwBkgnd>
<ShdwPattern>0</ShdwPattern>
<FillForegndTrans>{fg_trans}</FillForegndTrans>
<FillBkgndTrans>{bg_trans}</FillBkgndTrans>
<ShdwForegndTrans>0</ShdwForegndTrans>
<ShdwBkgndTrans>0</ShdwBkgndTrans>
</Fill>"""

def text_block() -> str:
    return """
<TextBlock>
<LeftMargin F='0.06DP'>0.06</LeftMargin>
<RightMargin F='0.06DP'>0.06</RightMargin>
<TopMargin F='0.03DP'>0.03</TopMargin>
<BottomMargin F='0.03DP'>0.03</BottomMargin>
<VerticalAlign F='1'>1</VerticalAlign>
<TextBkgnd F='0'>0</TextBkgnd>
<DefaultTabStop F='0.5DP'>0.5</DefaultTabStop>
<TextDirection F='0'>0</TextDirection>
<TextBkgndTrans F='0%'>0</TextBkgndTrans>
</TextBlock>"""

def xform(cx, cy, w, h) -> str:
    return f"""
<XForm>
<PinX>{cx}</PinX>
<PinY>{cy}</PinY>
<Width>{w}</Width>
<Height>{h}</Height>
<LocPinX F='Width*0.5'>{w/2}</LocPinX>
<LocPinY F='Height*0.5'>{h/2}</LocPinY>
<Angle>0</Angle>
<FlipX>0</FlipX>
<FlipY>0</FlipY>
<ResizeMode>0</ResizeMode>
</XForm>"""

def rect_geom(w, h, no_fill='0', no_line='0') -> str:
    return f"""
<Geom IX='0'>
<NoFill>{no_fill}</NoFill>
<NoLine>{no_line}</NoLine>
<NoShow>0</NoShow>
<NoSnap>0</NoSnap>
<MoveTo IX='1'><X F='Width*0'>0</X><Y F='Height*0'>0</Y></MoveTo>
<LineTo IX='2'><X F='Width*1'>{w}</X><Y F='Height*0'>0</Y></LineTo>
<LineTo IX='3'><X F='Width*1'>{w}</X><Y F='Height*1'>{h}</Y></LineTo>
<LineTo IX='4'><X F='Width*0'>0</X><Y F='Height*1'>{h}</Y></LineTo>
<LineTo IX='5'><X F='Geometry1.X1'>0</X><Y F='Geometry1.Y1'>0</Y></LineTo>
</Geom>"""

def diamond_geom(w, h) -> str:
    return f"""
<Geom IX='0'>
<NoFill>0</NoFill>
<NoLine>0</NoLine>
<NoShow>0</NoShow>
<NoSnap>0</NoSnap>
<MoveTo IX='1'><X>{w/2}</X><Y>{h}</Y></MoveTo>
<LineTo IX='2'><X>{w}</X><Y>{h/2}</Y></LineTo>
<LineTo IX='3'><X>{w/2}</X><Y>0</Y></LineTo>
<LineTo IX='4'><X>0</X><Y>{h/2}</Y></LineTo>
<LineTo IX='5'><X>{w/2}</X><Y>{h}</Y></LineTo>
</Geom>"""

def polyline_geom(points):
    lines = ["<Geom IX='0'>", "<NoFill>1</NoFill>", "<NoLine>0</NoLine>", "<NoShow>0</NoShow>", "<NoSnap>0</NoSnap>"]
    for i, (x, y) in enumerate(points, start=1):
        tag = 'MoveTo' if i == 1 else 'LineTo'
        lines.append(f"<{tag} IX='{i}'><X>{x}</X><Y>{y}</Y></{tag}>")
    lines.append("</Geom>")
    return '\n'.join(lines)

def register(name, kind, cx, cy, w, h):
    shapes_meta[name] = {'kind': kind, 'cx': cx, 'cy': cy, 'w': w, 'h': h}

def anchor(name, side):
    m = shapes_meta[name]
    cx, cy, w, h = m['cx'], m['cy'], m['w'], m['h']
    if side == 'left':
        return (cx - w/2, cy)
    if side == 'right':
        return (cx + w/2, cy)
    if side == 'top':
        return (cx, cy + h/2)
    if side == 'bottom':
        return (cx, cy - h/2)
    raise ValueError(side)

def rectangle(name, cx, cy, w, h, text='', fill='#FFFFFF', line='#404040', size=9, rounding='0.04'):
    global shape_id
    register(name, 'rect', cx, cy, w, h)
    text_xml = f"<Text><cp IX='0'/>{esc_text(text)}</Text>" if text else ""
    xml = f"""
<Shape ID='{shape_id}' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>
{xform(cx, cy, w, h)}
{line_block(color=line, rounding=rounding)}
{fill_block(fg=fill, bg=fill)}
{text_block()}
{char_block(size)}
{rect_geom(w, h)}
{text_xml}
</Shape>"""
    shape_id += 1
    return xml

def diamond(name, cx, cy, w, h, text, fill='#FFF3CD', line='#7A5C00', size=8):
    global shape_id
    register(name, 'diamond', cx, cy, w, h)
    xml = f"""
<Shape ID='{shape_id}' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>
{xform(cx, cy, w, h)}
{line_block(color=line, rounding='0')}
{fill_block(fg=fill, bg=fill)}
{text_block()}
{char_block(size)}
{diamond_geom(w, h)}
<Text><cp IX='0'/>{esc_text(text)}</Text>
</Shape>"""
    shape_id += 1
    return xml

def connector(points, color='#4B5563', weight='0.02', end_arrow='4'):
    global shape_id
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max(max_x - min_x, 0.05)
    h = max(max_y - min_y, 0.05)
    local_points = [(round(x - min_x, 4), round(y - min_y, 4)) for x, y in points]
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    xml = f"""
<Shape ID='{shape_id}' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>
{xform(cx, cy, w, h)}
{line_block(color=color, weight=weight, end_arrow=end_arrow, rounding='0')}
{fill_block(fg='#FFFFFF', bg='#FFFFFF', pattern='0')}
{polyline_geom(local_points)}
</Shape>"""
    shape_id += 1
    return xml

def label(cx, cy, text, size=8):
    global shape_id
    w, h = 0.35, 0.18
    xml = f"""
<Shape ID='{shape_id}' Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>
{xform(cx, cy, w, h)}
{line_block(color='#FFFFFF', weight='0.0', end_arrow='0', begin_arrow='0', rounding='0')}
{fill_block(fg='#FFFFFF', bg='#FFFFFF', pattern='0', fg_trans='100', bg_trans='100')}
{text_block()}
{char_block(size)}
{rect_geom(w, h, no_fill='1', no_line='1')}
<Text><cp IX='0'/>{esc_text(text)}</Text>
</Shape>"""
    shape_id += 1
    return xml

shapes = []
shapes.append(rectangle('lane_user_bg', 2.6, 6.15, 4.4, 10.7, fill='#F8FAFC', line='#CBD5E1', size=9))
shapes.append(rectangle('lane_skill_bg', 7.3, 6.15, 4.6, 10.7, fill='#F8FAFC', line='#CBD5E1', size=9))
shapes.append(rectangle('lane_ref_bg', 12.3, 6.15, 4.6, 10.7, fill='#F8FAFC', line='#CBD5E1', size=9))
shapes.append(rectangle('lane_user_hd', 2.6, 12.1, 4.4, 0.6, text='用户', fill='#DBEAFE', line='#60A5FA', size=11))
shapes.append(rectangle('lane_skill_hd', 7.3, 12.1, 4.6, 0.6, text='Skill 主流程', fill='#DCFCE7', line='#4ADE80', size=11))
shapes.append(rectangle('lane_ref_hd', 12.3, 12.1, 4.6, 0.6, text='参考资产', fill='#FEF3C7', line='#F59E0B', size=11))
shapes.append(rectangle('title', 8.0, 12.75, 6.8, 0.28, text='图标创意设计 Skill 流程泳道图（Visio）', fill='#FFFFFF', line='#FFFFFF', size=13, rounding='0'))

shapes.append(rectangle('u1', 2.6, 11.0, 2.8, 0.65, text='提供基础信息', fill='#FFFFFF', line='#2563EB'))
shapes.append(rectangle('u2', 2.6, 8.5, 2.8, 0.65, text='查看创意方向', fill='#FFFFFF', line='#2563EB'))
shapes.append(rectangle('u3', 2.6, 7.2, 2.8, 0.75, text='选择方向\n提出修改', fill='#FFFFFF', line='#2563EB'))
shapes.append(diamond('u4', 2.6, 5.9, 2.1, 0.9, text='需要风格变体？'))
shapes.append(rectangle('u5', 2.6, 4.6, 2.8, 0.75, text='对比并选定风格', fill='#FFFFFF', line='#2563EB'))
shapes.append(rectangle('u6', 2.6, 3.4, 2.8, 0.65, text='确认生成图标', fill='#FFFFFF', line='#2563EB'))
shapes.append(diamond('u7', 2.6, 2.2, 2.1, 0.9, text='是否满意结果？'))
shapes.append(rectangle('u8', 2.6, 1.0, 2.8, 0.65, text='接收最终图标', fill='#FFFFFF', line='#2563EB'))

shapes.append(diamond('s1', 7.3, 11.0, 2.1, 0.9, text='信息足够？'))
shapes.append(rectangle('s2', 6.0, 9.8, 2.3, 0.75, text='最多 1-2 轮追问', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s3', 8.6, 9.8, 2.3, 0.65, text='概念挖掘', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s4', 7.3, 8.5, 3.0, 0.85, text='输出 3-4 个\n创意方向', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s5', 7.3, 7.2, 3.0, 0.85, text='收集选择与\n修改意见', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s6', 6.0, 5.9, 2.3, 0.75, text='生成风格变体', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s7', 8.6, 5.9, 2.3, 0.75, text='确认最终方向', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s8', 7.3, 4.6, 3.0, 0.85, text='构建生图 Prompt', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s9', 7.3, 3.4, 3.0, 0.75, text='调用 image_gen', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s10', 7.3, 2.2, 3.0, 0.9, text='按反馈迭代\n最多 3 次', fill='#FFFFFF', line='#16A34A'))
shapes.append(rectangle('s11', 7.3, 1.0, 3.2, 0.85, text='提供使用建议 / SVG /\n尺寸参考', fill='#FFFFFF', line='#16A34A', size=8))

shapes.append(rectangle('r1', 12.3, 11.0, 3.2, 0.75, text='概念挖掘框架', fill='#FFFFFF', line='#D97706'))
shapes.append(rectangle('r2', 12.3, 9.8, 3.2, 0.75, text='视觉隐喻类型库', fill='#FFFFFF', line='#D97706'))
shapes.append(rectangle('r3', 12.3, 8.6, 3.2, 0.75, text='颜色心理学', fill='#FFFFFF', line='#D97706'))
shapes.append(rectangle('r4', 12.3, 7.4, 3.2, 0.75, text='图标风格指南', fill='#FFFFFF', line='#D97706'))
shapes.append(rectangle('r5', 12.3, 6.2, 3.2, 0.75, text='Prompt 模板库', fill='#FFFFFF', line='#D97706'))
shapes.append(rectangle('r6', 12.3, 5.0, 3.2, 0.75, text='质量评估标准', fill='#FFFFFF', line='#D97706'))

shapes.append(connector([anchor('u1', 'right'), anchor('s1', 'left')]))
shapes.append(connector([anchor('s1', 'bottom'), anchor('s2', 'top')]))
shapes.append(connector([anchor('s2', 'top'), (5.1, 10.6), (5.1, 11.0), anchor('s1', 'left')]))
shapes.append(connector([anchor('s1', 'right'), anchor('s3', 'top')]))
shapes.append(label(6.1, 11.15, '否'))
shapes.append(label(8.05, 11.15, '是'))

shapes.append(connector([anchor('s3', 'right'), anchor('r1', 'left')]))
shapes.append(connector([anchor('r1', 'bottom'), anchor('r2', 'top')], color='#B45309', weight='0.017'))
shapes.append(connector([anchor('r2', 'bottom'), anchor('r3', 'top')], color='#B45309', weight='0.017'))
shapes.append(connector([anchor('r3', 'bottom'), anchor('r4', 'top')], color='#B45309', weight='0.017'))
shapes.append(connector([anchor('r4', 'bottom'), anchor('r5', 'top')], color='#B45309', weight='0.017'))
shapes.append(connector([anchor('r5', 'bottom'), anchor('r6', 'top')], color='#B45309', weight='0.017'))
shapes.append(connector([anchor('r6', 'left'), (10.6, 5.0), (10.6, 8.5), anchor('s4', 'right')]))

shapes.append(connector([anchor('s4', 'left'), anchor('u2', 'right')]))
shapes.append(connector([anchor('u2', 'bottom'), anchor('u3', 'top')]))
shapes.append(connector([anchor('u3', 'right'), anchor('s5', 'left')]))
shapes.append(connector([anchor('s5', 'left'), anchor('u4', 'right')]))

shapes.append(connector([anchor('u4', 'right'), anchor('s6', 'left')]))
shapes.append(connector([anchor('u4', 'right'), (4.7, 5.9), (4.7, 5.2), (8.6, 5.2), anchor('s7', 'bottom')]))
shapes.append(label(4.85, 6.1, '是'))
shapes.append(label(5.0, 5.35, '否'))

shapes.append(connector([anchor('s6', 'right'), anchor('r4', 'left')]))
shapes.append(connector([anchor('r5', 'left'), (10.2, 6.2), (10.2, 4.6), anchor('u5', 'right')]))
shapes.append(connector([anchor('u5', 'right'), anchor('s7', 'left')]))

shapes.append(connector([anchor('s7', 'left'), anchor('u6', 'right')]))
shapes.append(connector([anchor('u6', 'right'), anchor('s8', 'left')]))
shapes.append(connector([anchor('s8', 'right'), anchor('r5', 'left')]))
shapes.append(connector([anchor('r5', 'left'), (10.0, 6.2), (10.0, 3.4), anchor('s9', 'right')]))
shapes.append(connector([anchor('s9', 'left'), anchor('u7', 'right')]))

shapes.append(connector([anchor('u7', 'right'), anchor('s10', 'left')]))
shapes.append(connector([anchor('u7', 'right'), (4.9, 2.2), (4.9, 1.0), anchor('s11', 'left')]))
shapes.append(label(5.0, 2.45, '否'))
shapes.append(label(5.0, 1.15, '是'))
shapes.append(connector([anchor('s10', 'top'), (9.4, 2.2), (9.4, 4.6), anchor('s8', 'right')]))
shapes.append(connector([anchor('s11', 'left'), anchor('u8', 'right')]))

shapes_xml = '\n'.join(shapes)
final_xml = prefix + '\n' + shapes_xml + '\n' + suffix
out_path.write_text(final_xml, encoding='utf-8')
print(out_path)
