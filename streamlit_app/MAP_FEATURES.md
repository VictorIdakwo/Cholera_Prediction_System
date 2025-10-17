# Interactive Map - Features & Controls

## 🗺️ Enhanced Map Features

### **Zoom & Pan Controls**

**Mouse Controls:**
- **Scroll Wheel** - Zoom in/out
- **Click & Drag** - Pan around the map
- **Double Click** - Zoom in on specific area
- **Shift + Drag** - Zoom to selected area

**Toolbar Buttons:**
- 🏠 **Home** - Reset to original view
- 📷 **Camera** - Download map as PNG (high resolution)
- ➕ **Zoom In** - Zoom closer
- ➖ **Zoom Out** - Zoom farther
- ↔️ **Pan** - Pan mode
- 🔍 **Box Zoom** - Select area to zoom
- 🔄 **Reset** - Reset axes

---

## 🎨 Improved Symbology

### **Color Scale (Yellow → Red)**

| Color | Hex Code | Meaning |
|-------|----------|---------|
| Very Light Yellow | `#ffffcc` | 0 cases (no risk) |
| Light Yellow | `#ffeda0` | Low cases |
| Yellow | `#fed976` | Moderate-low |
| Light Orange | `#feb24c` | Moderate |
| Orange | `#fd8d3c` | Moderate-high |
| Red-Orange | `#fc4e2a` | High |
| Red | `#e31a1c` | Very high |
| Dark Red | `#bd0026` | Extremely high |

**8-Step Gradient** for better visual distinction!

### **Enhanced Borders**
- **Width:** 2px (more visible)
- **Color:** White with transparency
- **Style:** Clean, modern look

### **Opacity**
- **Fill:** 80% (better color visibility)
- **Hover:** Highlighted on mouseover

---

## 📊 Map Styles (Selectable)

### **1. Light (Default)** 
- Clean white background
- Best for printing
- Easy to read labels
- Professional look

### **2. Dark**
- Dark background
- Great for presentations
- Reduces eye strain
- Modern aesthetic

### **3. Street**
- Shows street names
- Detailed road network
- Urban context visible
- Useful for navigation

### **4. Satellite**
- Aerial imagery
- Real terrain view
- Geographic context
- Natural features visible

---

## 💡 Hover Information

When you hover over any LGA, you see:

```
[LGA Name]
Predicted Cases: XXX.X
Actual Cases: XXX
```

**Features:**
- ✅ Bold LGA name
- ✅ Decimal precision for predictions
- ✅ Actual vs Predicted comparison
- ✅ Clean white tooltip background
- ✅ Easy-to-read font (Arial 13px)

---

## 📏 Color Legend

**Position:** Right side of map

**Features:**
- Title: "Predicted Cases"
- Gradient bar showing color scale
- Numerical values
- White background with border
- Professional styling

---

## 🎯 Map Title

**"Predicted Cholera Cases by LGA"**

- Centered at top
- Blue color (#1f77b4)
- White background with padding
- Always visible

---

## 🖼️ Export Options

**Download as PNG:**
- **Resolution:** 1200 × 800 pixels
- **Scale:** 2× (high quality)
- **Filename:** `cholera_map.png`
- **Format:** PNG (transparent background option)

**Perfect for:**
- Reports and presentations
- Publications
- Posters
- Social media

---

## 🎨 Visual Hierarchy

### **High Contrast**
- Dark borders (white) on colored areas
- Clear separation between LGAs
- Easy to distinguish regions

### **Readable Text**
- Large, bold titles
- Clear color legend
- Professional fonts

### **Professional Design**
- Clean layout
- Minimal clutter
- Focus on data

---

## 🔍 Zoom Levels

**Default Zoom:** 6.5 (optimal for viewing all LGAs)

**Recommended Zoom Levels:**
- **1-4:** State/country level
- **5-7:** Multi-LGA view (recommended)
- **8-10:** Single LGA focus
- **11-15:** Detailed local view

**Automatic centering** on data extent!

---

## 📱 Responsive Design

The map adapts to screen size:
- **Desktop:** Full width, 650px height
- **Tablet:** Scaled proportionally
- **Mobile:** Touch-friendly zoom/pan

---

## 🎓 Usage Tips

### **For Analysis:**
1. Start with default "Light" style
2. Zoom to area of interest
3. Hover to compare actual vs predicted
4. Switch to "Satellite" for geographic context

### **For Presentations:**
1. Use "Dark" style for projectors
2. Zoom to highlight specific LGAs
3. Download as PNG for slides
4. Use high-contrast colors

### **For Reports:**
1. Keep "Light" style
2. Standard zoom level (6.5)
3. Export at 2× scale
4. Include color legend

---

## 🔧 Technical Details

**Map Engine:** Plotly + Mapbox

**Data Format:** GeoJSON from shapefile

**Projection:** WGS84 (EPSG:4326)

**Rendering:** Client-side (fast, interactive)

**Performance:**
- Smooth zoom/pan
- Instant hover response
- Quick map style switching
- Efficient rendering

---

## 🆕 Recent Improvements (v1.1)

✅ **8-step color gradient** (was 2-step)
✅ **Thicker borders** (2px vs 1px)
✅ **Better opacity** (80% vs 70%)
✅ **Map style selector** (4 options)
✅ **Enhanced hover tooltips**
✅ **Professional color legend**
✅ **Map title**
✅ **High-res export** (1200×800, 2× scale)
✅ **Improved zoom controls**
✅ **Better initial positioning**

---

## 🎉 Interactive Features Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Zoom** | Scroll or toolbar | See details |
| **Pan** | Click & drag | Explore area |
| **Hover** | Mouse over LGA | See data |
| **Style** | 4 map styles | Context switching |
| **Export** | PNG download | Share/report |
| **Legend** | Color scale | Interpret data |
| **Title** | Map description | Clear context |
| **Borders** | White outlines | Clear boundaries |

---

**The map is now fully interactive with professional symbology!** 🎨🗺️✨
