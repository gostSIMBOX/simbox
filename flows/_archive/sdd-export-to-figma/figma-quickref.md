# Figma Quick Reference: GOSTsimbox Gateway

> Quick-start guide for building the design system in Figma
> Figma File: https://www.figma.com/design/FUBZIOMUleEqSDgQiuibXD/Telon

---

## Getting Started

1. **Open Figma file**: https://www.figma.com/design/FUBZIOMUleEqSDgQiuibXD/Telon
2. **Duplicate the page** (optional but recommended): Right-click page → "Duplicate page"
3. **Rename** to "📱 GOSTsimbox Gateway"

---

## Phase 1: Design System (1h 15m)

### Step 1: Create Color Styles (30 min)

**Open Local Styles panel**: Left sidebar → Styles icon (⚡) → "+" → "Color style"

Create these 16 colors:

```
Background Colors:
  🎨 GOSTsimbox/Background/Primary    → #1A1A1A
  🎨 GOSTsimbox/Background/Surface    → #2A2A2A

Primary Colors:
  🎨 GOSTsimbox/Primary/Main          → #1E88E5
  🎨 GOSTsimbox/Primary/Light         → #42A5F5
  🎨 GOSTsimbox/Primary/Dark          → #1565C0

Semantic Colors:
  🎨 GOSTsimbox/Success/Main          → #10B981
  🎨 GOSTsimbox/Warning/Main          → #F59E0B
  🎨 GOSTsimbox/Error/Main            → #EF4444
  🎨 GOSTsimbox/Info/Main             → #3B82F6
  🎨 GOSTsimbox/Debug/Main            → #9CA3AF

Text Colors:
  🎨 GOSTsimbox/Text/Primary          → #FFFFFF
  🎨 GOSTsimbox/Text/Secondary        → #9CA3AF
  🎨 GOSTsimbox/Text/Disabled         → #6B7280

Border Colors:
  🎨 GOSTsimbox/Border/Default        → #404040
  🎨 GOSTsimbox/Border/Focused        → #1E88E5
  🎨 GOSTsimbox/Border/Error          → #EF4444
```

**Pro tip**: Create a reference frame with all colors as rectangles for visual reference.

---

### Step 2: Create Text Styles (30 min)

**Create Text Style**: Select text → Right sidebar → Text styles → "+" → "Create style"

Font family for all: **Poppins**

```
📝 GOSTsimbox/Display
    Size: 28, Weight: Bold, Line height: 36, Color: #FFFFFF

📝 GOSTsimbox/Headline/Large
    Size: 24, Weight: Bold, Line height: 32, Color: #FFFFFF

📝 GOSTsimbox/Headline/Medium
    Size: 20, Weight: SemiBold, Line height: 28, Color: #FFFFFF

📝 GOSTsimbox/Headline/Small
    Size: 18, Weight: SemiBold, Line height: 24, Color: #FFFFFF

📝 GOSTsimbox/Body/Large
    Size: 16, Weight: Regular, Line height: 24, Color: #FFFFFF

📝 GOSTsimbox/Body/Medium
    Size: 14, Weight: Regular, Line height: 20, Color: #FFFFFF

📝 GOSTsimbox/Body/Small
    Size: 12, Weight: Regular, Line height: 16, Color: #FFFFFF

📝 GOSTsimbox/Button/Large
    Size: 16, Weight: SemiBold, Line height: 24, Color: #FFFFFF

📝 GOSTsimbox/Button/Medium
    Size: 14, Weight: SemiBold, Line height: 20, Color: #FFFFFF

📝 GOSTsimbox/Label
    Size: 12, Weight: Medium, Line height: 16, Color: #9CA3AF
```

**Pro tip**: Install Google Fonts plugin if Poppins isn't available.

---

### Step 3: Create Effect Styles (15 min)

**Create Effect Style**: Right sidebar → Effects → "+" → Create style

```
💡 GOSTsimbox/Shadow/Small
    Drop shadow: X=0, Y=1, Blur=2, Spread=0, Color=#000000 10%

💡 GOSTsimbox/Shadow/Medium
    Drop shadow: X=0, Y=2, Blur=4, Spread=0, Color=#000000 15%

💡 GOSTsimbox/Shadow/Large
    Drop shadow: X=0, Y=4, Blur=8, Spread=0, Color=#000000 20%

💡 GOSTsimbox/Shadow/XL
    Drop shadow: X=0, Y=8, Blur=16, Spread=0, Color=#000000 25%
```

---

## Phase 2: Components (3h)

### Component 1: Primary Button

1. **Create frame**: 200×48
2. **Add rectangle**: Fill=`#1E88E5`, Corner radius=8
3. **Add text**: "Connect", Style=Button/Large, Color=`#FFFFFF`
4. **Auto layout**: Shift+A, Padding=24×12
5. **Create component**: Ctrl+Alt+K (Cmd+Option+K Mac)
6. **Add variants**:
   - Hover: Fill=`#42A5F5`
   - Disabled: Fill=`#404040`, Text=`#6B7280`
   - Loading: Add spinner icon

**Variant property**: `State` = Default | Hover | Disabled | Loading

---

### Component 2: Input Field

1. **Create frame**: 358×60
2. **Add rectangle**: Fill=`#2A2A2A`, Stroke=`#404040`, Radius=12
3. **Add icon**: 24×24, left padding=16
4. **Add label**: Style=Label, top margin=4
5. **Add text input**: Style=Body/Large, left padding=16
6. **Create component + variants**

**Variant properties**: 
- `State` = Default | Focused | Error | Disabled
- `Has Icon` = True | False
- `Has Label` = True | False

---

### Component 3: Card

1. **Create frame**: 358×auto
2. **Add rectangle**: Fill=`#2A2A2A`, Radius=12, Effect=Shadow/Medium
3. **Auto layout**: Padding=16, Gap=12
4. **Create component**

---

### Component 4: Status Badge

1. **Create frame**: Auto width×20
2. **Add rectangle**: Fill=`#10B98120` (20% opacity), Radius=4
3. **Add text**: "SUCCESS", Style=Label, Color=`#10B981`
4. **Auto layout**: Padding=6×2
5. **Create component + variants**

**Variant property**: `Level` = Success | Warning | Error | Info | Debug

---

### Component 5: Status Card

1. **Create frame**: 114×96
2. **Add rectangle**: Fill=`#2A2A2A`, Radius=8, Effect=Shadow/Small
3. **Add icon**: 28×28, top center
4. **Add title**: "SIP", Style=Label, Color=`#9CA3AF`
5. **Add value**: "Connected", Style=Headline/Small, Color=`#10B981`
6. **Auto layout**: Padding=16, Gap=8
7. **Create component**

---

### Component 6: Info Row

1. **Create auto layout frame**: Horizontal
2. **Add label**: "Phone Number", Style=Body/Medium, Color=`#9CA3AF`
3. **Add spacer**: Flex=1
4. **Add value**: "+1234567890", Style=Body/Medium, Color=`#FFFFFF`
5. **Padding**: 4 vertical
6. **Create component**

---

### Component 7: FAB (Floating Action Button)

1. **Create circle**: 56×56, Fill=`#1E88E5`
2. **Add icon**: 24×24, center, Color=`#FFFFFF`
3. **Create component + variants**

**Variant properties**:
- `Type` = Regular | Extended
- `Icon` = play_arrow | stop | add | etc.
- `State` = Default | Hover | Disabled

---

### Component 8: AppBar

1. **Create frame**: 390×56
2. **Add background**: Fill=`#1A1A1A` or transparent
3. **Add title**: "Dashboard", Style=Headline/Medium
4. **Add action icons slot**: Right side, 24×24
5. **Create component**

---

## Phase 3: Screens (~8h)

### Screen Template

For each screen:

1. **Create frame**: 390×844 (iPhone 13)
2. **Name**: "XX Screen Name" (e.g., "01 Auth Screen")
3. **Add background**: Fill=`#1A1A1A`
4. **Add SafeArea**: Top=47, Bottom=34 (iPhone 13)
5. **Use auto layout**: Vertical, Gap=16
6. **Use components** from library
7. **Follow structure** from specifications (02-specifications.md)

---

### Screen Order & Priority

**Priority 1 (Core - do first):**
1. 01 Auth Screen
2. 02 Dashboard Screen
3. 03 Settings Screen
4. 04 Logs Screen

**Priority 2 (Main flows):**
5-7. Call Management (3 screens)
8-11. SMS & Messaging (4 screens)

**Priority 3 (Feature screens):**
12-17. Voice Line (6 screens)
18-25. Dongle (8 screens)

**Priority 4 (Secondary):**
26-28. SIP & Network (3 screens)
29-33. Configuration (5 screens)
34-36. Other (3 screens)

---

## Phase 4: Organization (2h)

### Create Sections

Right-click canvas → "Create section" → Name:

```
📁 🎨 Design System
📁 📱 Core Gateway
📁 📞 Call Management
📁 💬 SMS & Messaging
📁 🎤 Voice Line
📁 🔌 Dongle
📁 🌐 SIP & Network
📁 ⚙️ Configuration
📁 📁 Other
```

### Organize Frames

Drag each frame into its section.

### Create Cover Frame

1. **Create frame**: 1200×800
2. **Add title**: "GOSTsimbox Gateway Design System"
3. **Add version**: "v1.0 - 2026-03-11"
4. **Add screen index**: List all 37 screens with numbers
5. **Place at top** of page

---

## Keyboard Shortcuts

| Action | Windows | Mac |
|--------|---------|-----|
| Create component | Ctrl+Alt+K | Cmd+Option+K |
| Auto layout | Shift+A | Shift+A |
| Frame | F | F |
| Rectangle | R | R |
| Text | T | T |
| Duplicate | Ctrl+D | Cmd+D |
| Group | Ctrl+G | Cmd+G |
| Lock | Ctrl+Shift+L | Cmd+Shift+L |

---

## Plugins to Install

1. **Google Fonts** - For Poppins font
2. **Material Design Icons** - For icons
3. **Autoflow** - For prototyping arrows
4. **Sticky Notes** - For annotations

---

## Checklist

### Design System Complete When:
- [ ] 16 Color Styles created
- [ ] 10 Text Styles created
- [ ] 4 Effect Styles created

### Components Complete When:
- [ ] 8 component sets created
- [ ] All variants working
- [ ] Components tested in sample frames

### Screens Complete When:
- [ ] 37 screen frames created
- [ ] All use components (not raw shapes)
- [ ] Auto layout applied
- [ ] Layers named clearly

### Organization Complete When:
- [ ] 9 sections created
- [ ] All frames in correct sections
- [ ] Cover/index frame added
- [ ] Share link generated

---

## Troubleshooting

**Q: Text style not showing Poppins?**
A: Install Google Fonts plugin or use sans-serif fallback.

**Q: Component variants not working?**
A: Make sure you're in the component master, use "Variant" property in right sidebar.

**Q: Auto layout breaking design?**
A: Check padding and gap values, use "Fill container" for flexible widths.

**Q: Colors not matching?**
A: Verify hex codes, check opacity is 100%.

---

## Next Steps After Completion

1. **Share**: Click "Share" → "Copy link" → Set to "Anyone with link can view"
2. **Export**: File → Export → PDF (for documentation)
3. **Prototype**: Connect screens if creating interactive demo
4. **Document**: Add notes for developers (Dev Mode)

---

**Good luck! 🚀**

Take breaks every hour. This is detailed work that requires focus.
