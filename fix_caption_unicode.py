from pathlib import Path
p=Path('caption_bridge.lua');s=p.read_text(encoding='utf-8');s=s.replace('local function clean(text)','''local charPattern='[%z\\1-\\127\\194-\\244][\\128-\\191]*'
local function letters(text)
 local out={};for ch in text:gmatch(charPattern) do table.insert(out,ch) end;return out
end
local function charlen(text) return #letters(text) end
local function clean(text)''');s=s.replace('for _,cp in utf8.codes(text) do\n  local ch=utf8.char(cp)', '''for _,ch in ipairs(letters(text)) do
  local b={ch:byte(1,#ch)};local cp=b[1]
  if #b==2 then cp=(b[1]-192)*64+b[2]-128
  elseif #b==3 then cp=(b[1]-224)*4096+(b[2]-128)*64+b[3]-128
  elseif #b==4 then cp=(b[1]-240)*262144+(b[2]-128)*4096+(b[3]-128)*64+b[4]-128 end''');s=s.replace('utf8.len','charlen');s=s.replace("local cut=utf8.offset(word,16);table.insert(lines,word:sub(1,cut-1));word=word:sub(cut)","local chars=letters(word);table.insert(lines,table.concat(chars,'',1,15));word=table.concat(chars,'',16,#chars)");p.write_text(s,encoding='utf-8')
