# 🏢 Logos de EURO SECURITY

Esta carpeta contiene los logos oficiales de la empresa.

## 📁 Archivos requeridos:

### Logos principales:
- `euro-security-logo.png` - Logo principal (recomendado: 300x100px)
- `euro-security-icon.png` - Icono cuadrado (recomendado: 64x64px)
- `euro-security-white.png` - Logo blanco para fondos oscuros (300x100px)
- `favicon.ico` - Icono del navegador (32x32px)

### Especificaciones técnicas:
- **Formato**: PNG con transparencia (excepto favicon que debe ser ICO)
- **Resolución**: Mínimo 150 DPI para impresión
- **Colores**: Mantener colores corporativos consistentes

### Uso en templates:
```html
<!-- Logo principal -->
<img src="{{ branding.logos.main }}" alt="{{ branding.company_name }}">

<!-- Icono -->
<img src="{{ branding.logos.icon }}" alt="{{ branding.company_name }}">

<!-- Logo blanco -->
<img src="{{ branding.logos.white }}" alt="{{ branding.company_name }}">
```

## 🎨 Colores corporativos:
- **Azul principal**: #1e40af
- **Púrpura**: #7c3aed
- **Verde**: #059669
