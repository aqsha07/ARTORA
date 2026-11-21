"""
ARTORA Database Seeder
Populates categories, rich product catalog, sample reviews, and default test accounts.
Brand: ARTORA - Create Without Limits.
"""

from app import create_app
from app.extensions import db
from app.models.user import User, Address
from app.models.product import Category, Product, ProductImage, Review, slugify

app = create_app()

CATEGORIES_DATA = [
    {
        "name": "Canvas and Painting Surfaces",
        "tagline": "Premium Belgian linen, triple-primed cotton, and archival hardwood panels.",
        "description": "Engineered for superior tension, tactile tooth, and decades of archival longevity. Suitable for heavy body oils, acrylics, and mixed media.",
        "icon_class": "fa-square",
        "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80",
        "display_order": 1,
        "is_featured": True
    },
    {
        "name": "Acrylic Paints",
        "tagline": "Pure pigment loads with buttery viscosity and brilliant lightfastness.",
        "description": "Heavy body, fluid, and gouache formulations crafted with 100% acrylic polymer emulsion for zero color-shift upon drying.",
        "icon_class": "fa-paint-roller",
        "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=800&q=80",
        "display_order": 2,
        "is_featured": True
    },
    {
        "name": "Oil Paints",
        "tagline": "Cold-pressed linseed oils triple-milled with single, luminescent pigments.",
        "description": "Rich, buttery, and slow-drying artist-grade oil colors that capture subtle tonal gradations and masterwork depth.",
        "icon_class": "fa-palette",
        "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80",
        "display_order": 3,
        "is_featured": True
    },
    {
        "name": "Watercolor Paints",
        "tagline": "Luminous honey-bound watercolor pans and vibrant pure tubes.",
        "description": "Micro-milled mineral and botanical pigments ground with pure gum arabic and kordofan honey for radiant washes and granulating effects.",
        "icon_class": "fa-droplet",
        "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80",
        "display_order": 4,
        "is_featured": True
    },
    {
        "name": "Paint Brushes",
        "tagline": "Handmade Kolinsky sables, Japanese hakes, and synthetic micro-filberts.",
        "description": "Seamless nickel-plated brass ferrules balanced on FSC-certified hardwood handles for responsive snap and controlled flow.",
        "icon_class": "fa-paintbrush",
        "image_url": "https://images.unsplash.com/photo-1525909002-1b05e0c869d8?auto=format&fit=crop&w=800&q=80",
        "display_order": 5,
        "is_featured": True
    },
    {
        "name": "Drawing and Sketching",
        "tagline": "Archival graphite grades, willow vine charcoals, and fine pigments.",
        "description": "From 9B velvety darks to 9H precision technical graphites, rich compressed charcoal blocks, and pigmented fineliners.",
        "icon_class": "fa-pen-nib",
        "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=800&q=80",
        "display_order": 6,
        "is_featured": True
    },
    {
        "name": "Art Papers and Sketchbooks",
        "tagline": "100% cotton rag, mould-made blocks, and smyth-sewn artist journals.",
        "description": "Deckled edge cold-pressed sheets, hot-pressed botanical blocks, and mixed-media lay-flat hardbound journals.",
        "icon_class": "fa-book-open",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80",
        "display_order": 7,
        "is_featured": True
    },
    {
        "name": "Easels and Painting Tools",
        "tagline": "Beechwood studio cranks, French plein-air boxes, and spring-steel knives.",
        "description": "Rock-solid studio workhorses, compact brass-fitted travel easels, mahl sticks, and flexible palette knives.",
        "icon_class": "fa-wrench",
        "image_url": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=800&q=80",
        "display_order": 8,
        "is_featured": False
    },
    {
        "name": "DIY and Craft Supplies",
        "tagline": "Polymer modeling clays, linocut printmaking gouges, and resin kits.",
        "description": "Tactile creative mediums including gold leaf gilding, Japanese block printing blocks, carving gouges, and epoxy systems.",
        "icon_class": "fa-shapes",
        "image_url": "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=800&q=80",
        "display_order": 9,
        "is_featured": False
    },
    {
        "name": "Artist Accessories",
        "tagline": "Ceramic wells, brass brush washers, wax canvas rollups, and studio aprons.",
        "description": "Thoughtfully crafted tactile accompaniments designed to bring calm organization and enduring beauty to your creative sanctum.",
        "icon_class": "fa-bag-shopping",
        "image_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=800&q=80",
        "display_order": 10,
        "is_featured": False
    },
    {
        "name": "Art Kits and Combos",
        "tagline": "Curated master gift sets, beginner discovery chests, and plein-air bundles.",
        "description": "Harmoniously paired collections containing matching pigments, surfaces, brushes, and mediums in handcrafted wooden cases.",
        "icon_class": "fa-gift",
        "image_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=800&q=80",
        "display_order": 11,
        "is_featured": True
    }
]

PRODUCTS_DATA = [
    # 1. Canvas and Painting Surfaces
    {
        "category": "Canvas and Painting Surfaces",
        "name": "Master Belgian Stretched Linen Canvas (16x20 in)",
        "brand": "ARTORA Atelier",
        "price": 1499.00,
        "compare_at_price": 1899.00,
        "stock": 42,
        "badge": "Bestseller",
        "short_description": "Custom hand-stretched 100% unbleached Belgian linen with quadruple titanium gesso priming on kiln-dried pine stretcher bars.",
        "description": "Our flagship linen canvas is woven from long-fiber European flax to provide unmatched tensile strength and organic texture. Triple-gessoed by hand to offer the ideal tooth for both glaze-heavy oil paintings and impasto acrylic applications. Reinforced with tongue-and-groove corner keys.",
        "specifications": "Material: 100% Belgian Linen\nSize: 16 x 20 inches (40 x 50 cm)\nProfile Depth: 1.5 inch Gallery Stretcher\nPriming: Acid-free Titanium Gesso (4 coats)\nWood: Kiln-dried Scandinavian Pine",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Canvas and Painting Surfaces",
        "name": "Heavyweight Cotton Canvas Panels (Pack of 6, 10x12 in)",
        "brand": "ARTORA Studio",
        "price": 799.00,
        "compare_at_price": 999.00,
        "stock": 80,
        "badge": "Artisan Choice",
        "short_description": "Rigid warp-resistant MDF core wrapped in 380 GSM pure cotton canvas, perfect for plein-air studies and daily practice.",
        "description": "Designed for artists on the move, these sturdy panels eliminate sagging and puncture risks. Pre-primed with neutral white acrylic gesso, ready for immediate brushwork out of the packaging.",
        "specifications": "Core: 3.5mm Archival Hardboard\nWeight: 380 GSM Duck Cotton\nQuantity: 6 Panels per Pack\nTexture: Medium Grain",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Canvas and Painting Surfaces",
        "name": "Natural Birch Wood Cradled Art Board (12x12 in)",
        "brand": "Nordic Woodcraft",
        "price": 649.00,
        "compare_at_price": 750.00,
        "stock": 35,
        "badge": "New Arrival",
        "short_description": "Silky-smooth sanded Baltic birch plywood surface mounted to a solid pine support cradle for fluid acrylics, resin, and pyrography.",
        "description": "Offers an uncompromisingly rigid ground with stunning natural wood grain that can either be primed with clear gesso to celebrate the grain or coated with white ground.",
        "specifications": "Face: Grade A Baltic Birch\nCradle Depth: 1.25 inches\nGrain: Fine Satin Sanded\nSize: 12 x 12 inches",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 2. Acrylic Paints
    {
        "category": "Acrylic Paints",
        "name": "Master Artist Heavy Body Acrylic Set (12 x 75ml)",
        "brand": "ARTORA Atelier",
        "price": 1899.00,
        "compare_at_price": 2499.00,
        "stock": 55,
        "badge": "Bestseller",
        "short_description": "High-viscosity artist acrylics with exceptionally high pigment loading and rich impasto retention.",
        "description": "Formulated with single pigments and flexible 100% acrylic emulsion. Holds knife marks and peaks with crisp definition, drying to a consistent satin finish without darkening or yellowing over time.",
        "specifications": "Palette: 12 Primary & Earth Tones\nVolume: 75 ml Tubes\nViscosity: Heavy Body Buttery\nLightfastness: ASTM I & II\nFinish: Satin",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Acrylic Paints",
        "name": "Professional Acrylic Gouache Velvet Set (18 x 20ml)",
        "brand": "Chroma Artisans",
        "price": 1650.00,
        "compare_at_price": 1950.00,
        "stock": 38,
        "badge": "Top Pick",
        "short_description": "Ultra-matte opaque acrylic gouache that dries water-resistant without bleeding or muddying subsequent layers.",
        "description": "Combines the velvety flat finish of traditional designer gouache with the permanent flexibility of acrylics. Exceptional covering power for botanical illustration, character design, and bold graphic canvases.",
        "specifications": "Finish: Dead-Matte Velveteen\nSolubility: Permanent once dry\nCount: 18 Tubes (20ml each)\nBase: Waterborne Polymer",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Acrylic Paints",
        "name": "Luminescent Metallic & Iridescent Acrylic Tubes (6 x 60ml)",
        "brand": "ARTORA Studio",
        "price": 999.00,
        "compare_at_price": 1250.00,
        "stock": 28,
        "badge": "New Arrival",
        "short_description": "Formulated with pure mica powders in Rich Gold, Antique Bronze, Rose Gold, Sterling Silver, Copper, and Pearl White.",
        "description": "Catch light with breathtaking micro-shimmer. Non-tarnishing mineral micas suspended in crystal-clear gloss vehicle for accents, backgrounds, and mixed-media gilding effects.",
        "specifications": "Colors: Gold, Bronze, Copper, Silver, Rose Gold, Pearl\nVolume: 60 ml\nFinish: Lustrous Shimmer",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 3. Oil Paints
    {
        "category": "Oil Paints",
        "name": "Florentine Artist Oil Color Wooden Chest (10 x 40ml + Mediums)",
        "brand": "Florentine Masterworks",
        "price": 3499.00,
        "compare_at_price": 4299.00,
        "stock": 19,
        "badge": "Artisan Choice",
        "short_description": "Slow-dried cold-pressed Swedish linseed oil ground with single historical and modern pigments in an engraved walnut presentation box.",
        "description": "Prized by portrait and landscape masters for remarkable tinting strength, buttery spreadability, and luminous glazing transparency. Includes Purified Linseed Oil (75ml) and Odorless Thinner (75ml).",
        "specifications": "Tubes: 10 Master Colors (40ml)\nMediums: Cold-pressed Linseed Oil & Mineral Solvent\nBox: Finished Walnut Wood with Brass Latches\nLightfastness: Guaranteed 100+ years",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Oil Paints",
        "name": "Titanium White Master Oil Paint (Jumbo 200ml Tube)",
        "brand": "ARTORA Atelier",
        "price": 899.00,
        "compare_at_price": 1100.00,
        "stock": 65,
        "badge": "Studio Classic",
        "short_description": "The quintessential studio workhorse white. Pure PW6 pigment milled in non-yellowing safflower oil for maximum brilliance.",
        "description": "Never run out of your most essential color. Formulated with high tinting strength to cleanly raise values without muddying delicate color temperatures.",
        "specifications": "Pigment: PW6 (Titanium Dioxide)\nOil Binder: Refined Safflower Oil\nVolume: 200 ml\nOpacity: Maximum Opaque",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 4. Watercolor Paints
    {
        "category": "Watercolor Paints",
        "name": "Botanical Honey Watercolor Palette (24 Half-Pans in Enamel Tin)",
        "brand": "ARTORA Botanicals",
        "price": 2299.00,
        "compare_at_price": 2899.00,
        "stock": 34,
        "badge": "Bestseller",
        "short_description": "Pure acacia gum and wild forest honey formulation yielding instant re-wettability, luminous flow, and mesmerizing granulating textures.",
        "description": "Hand-poured into durable half pans and presented in a classic travel tin with fold-out mixing wells. Specifically curated for botanical illustrators, landscape painters, and urban sketchers.",
        "specifications": "Format: 24 Half Pans\nBinder: Pure Gum Arabic & Wild Forest Honey\nTin: Heavy Enamel Metal with Thumb Ring\nGranulation: Selected Multi-Pigment Sediments",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Watercolor Paints",
        "name": "Granulating Mineral Watercolor Tube Set (6 x 15ml)",
        "brand": "Terra Mineralia",
        "price": 1450.00,
        "compare_at_price": 1750.00,
        "stock": 25,
        "badge": "Artisan Choice",
        "short_description": "Rare earth minerals: Lapis Lazuli, Green Jasper, Hematite Burnt Scarlet, Sodalite, Piemontite, and Tiger's Eye.",
        "description": "These genuine geological mineral pigments separate into stunning sedimentary textures when floated with water, creating organic atmospheric landscapes automatically.",
        "specifications": "Origin: Natural semi-precious stone ores\nVolume: 6 x 15ml\nProperty: Super-granulating sedimentary\nBinder: Kordofan Gum Arabic",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 5. Paint Brushes
    {
        "category": "Paint Brushes",
        "name": "Heritage Master Kolinsky Sable Brush Trio (#2, #6, #10)",
        "brand": "ARTORA Heritage",
        "price": 2199.00,
        "compare_at_price": 2699.00,
        "stock": 30,
        "badge": "Artisan Choice",
        "short_description": "Finest winter male Kolinsky hair with needle-sharp points, enormous reservoir capacity, and energetic spring.",
        "description": "Hand-cupped and tied by generational brushmakers. Seamless nickel brass ferrules anchored to satin charcoal birch handles with copper wire windings. The definitive watercolorist instrument.",
        "specifications": "Hair: 100% Selected Siberian Kolinsky\nSizes: Round #2, Round #6, Round #10\nHandle: Ergonomic Satin Birchwood\nFerrule: Seamless Double-Crimped Nickel Plated",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1525909002-1b05e0c869d8?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Paint Brushes",
        "name": "Chungking Hog Bristle Filbert & Flat Set (6 Brushes)",
        "brand": "ARTORA Studio",
        "price": 1199.00,
        "compare_at_price": 1499.00,
        "stock": 45,
        "badge": "Bestseller",
        "short_description": "Interlocked natural white bristles with split ends (flags) that hold vast reserves of heavy paint for bold mark-making.",
        "description": "Engineered for thick oil and acrylic applications. Long hardwood handles permit loose, gestural arm movements from easel distance.",
        "specifications": "Hair: Pure Double-Boiled Chungking Hog Bristle\nSizes: Flats #4, #8, #12; Filberts #2, #6, #10\nHandle: Long Matte Terracotta Beechwood",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1525909002-1b05e0c869d8?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Paint Brushes",
        "name": "Japanese Sheep Hair Hake Wash Brush (2.5 Inch)",
        "brand": "Kyoto Tools",
        "price": 699.00,
        "compare_at_price": 850.00,
        "stock": 50,
        "badge": "Top Pick",
        "short_description": "Soft natural goat hair hand-stitched into a flat raw bamboo handle for wide atmospheric washes and dampening large paper sheets.",
        "description": "Holds immense volumes of liquid wash without dripping prematurely. Stitched with copper wire through perforated natural bamboo.",
        "specifications": "Width: 2.5 inches (65mm)\nHair: Unbleached Natural Sheep Wool\nHandle: Raw Split Bamboo",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1525909002-1b05e0c869d8?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 6. Drawing and Sketching
    {
        "category": "Drawing and Sketching",
        "name": "Archival Graphite & Charcoal Master Metal Tin (24 Pieces)",
        "brand": "ARTORA Studio",
        "price": 1199.00,
        "compare_at_price": 1599.00,
        "stock": 60,
        "badge": "Bestseller",
        "short_description": "Full gradient from 9B to 9H cedar pencils, woodless graphite sticks, willow vine charcoals, kneaded eraser, and tortillions.",
        "description": "From razor-sharp technical drafting lines to smoky chiaroscuro shadows, this complete kit equips students and professionals for figure drawing, architectural sketching, and fine art portraits.",
        "specifications": "Contents: 12 Graphite Pencils (9B-9H), 4 Compressed Charcoals, 3 Woodless Sticks, 2 Blending Stumps, Kneaded Eraser, Brass Sharpener\nCasing: Embossed Brushed Metal Tin",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Drawing and Sketching",
        "name": "Archival Micron Waterproof Fineliner Pen Set (8 Nib Sizes)",
        "brand": "Precision Line",
        "price": 799.00,
        "compare_at_price": 999.00,
        "stock": 75,
        "badge": "Top Pick",
        "short_description": "Pigment-based black ink that is completely waterproof, fade-proof, and chemical-resistant. 0.05mm to 1.0mm + Brush tip.",
        "description": "The gold standard for ink-and-wash paintings, comic inks, and architectural journaling. Will not smear even under wet watercolor washes.",
        "specifications": "Nibs: 005 (0.2mm), 01 (0.25mm), 02 (0.3mm), 03 (0.35mm), 05 (0.45mm), 08 (0.5mm), 10 (0.6mm), Brush\nInk: Archival Pigment Pigma Ink\nSafety: Non-toxic, Acid-free",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 7. Art Papers and Sketchbooks
    {
        "category": "Art Papers and Sketchbooks",
        "name": "100% Cotton Cold-Pressed Watercolor Block (300 GSM, 9x12 in)",
        "brand": "ARTORA Papermill",
        "price": 1399.00,
        "compare_at_price": 1699.00,
        "stock": 48,
        "badge": "Bestseller",
        "short_description": "Mould-made 100% cotton rag with gelatin surface sizing. Glued on all 4 sides so paper remains flat during heavy saturation.",
        "description": "Crafted on cylindrical moulds to achieve irregular, organic grain. Resists scraping and lifting without tearing, delivering vivid color reflections.",
        "specifications": "Fiber: 100% Long Cotton Fibers\nWeight: 300 GSM (140 lb)\nSheets: 20 Sheets Glued on 4 Edges\nTexture: Cold Pressed / Not Grain",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Art Papers and Sketchbooks",
        "name": "Terracotta Hardcover Lay-Flat Mixed Media Journal (A5, 250 GSM)",
        "brand": "ARTORA Atelier",
        "price": 899.00,
        "compare_at_price": 1099.00,
        "stock": 55,
        "badge": "New Arrival",
        "short_description": "Warm ivory Italian paper with smyth-sewn binding that opens completely flat across double-page landscape spreads.",
        "description": "Bound in tactile natural terracotta bookcloth with ribbon bookmark and elastic closure. Heavyweight enough for light washes, gouache, colored pencil, and collage.",
        "specifications": "Size: A5 (5.8 x 8.3 inches)\nPages: 120 Pages (60 Leaves)\nPaper: 250 GSM Heavy French Vellum\nCover: Woven Terracotta Bookcloth with Gold Foil",
        "is_featured": True,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 8. Easels and Painting Tools
    {
        "category": "Easels and Painting Tools",
        "name": "Oiled Beechwood Studio H-Frame Crank Easel",
        "brand": "Verona Woodcraft",
        "price": 4499.00,
        "compare_at_price": 5499.00,
        "stock": 14,
        "badge": "Artisan Choice",
        "short_description": "Sturdy European steamed beechwood with smooth brass ratchet mast supporting canvases up to 60 inches high.",
        "description": "Built for a lifetime in the active artist studio. Wide base with rubber non-slip dampeners and spacious double utility trays for brushes, palette cups, and rag storage.",
        "specifications": "Material: Steamed European Beechwood (Stained & Oiled)\nMax Canvas Height: 155 cm (61 inches)\nBase Footprint: 55 x 50 cm\nWeight: 8.5 kg\nAdjustment: Ratchet Crank Mast",
        "is_featured": True,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Easels and Painting Tools",
        "name": "Spring-Steel Artist Palette Knife Set (5 Shapes)",
        "brand": "ARTORA Studio",
        "price": 549.00,
        "compare_at_price": 699.00,
        "stock": 70,
        "badge": "Top Pick",
        "short_description": "Forged single-piece flexible Italian spring steel blades with ergonomic rosewood handles and brass collars.",
        "description": "Angled offset crank keeps knuckles safely off the wet painting surface. Ideal for mixing colors cleanly on the palette and applying thick impasto layers.",
        "specifications": "Blade: Tempered Stainless Spring Steel\nHandle: Oiled Rosewood with Brass Ferrule\nShapes: Teardrop, Long Blade, Offset Diamond, Spatula, Pointed Trowel",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 9. DIY and Craft Supplies
    {
        "category": "DIY and Craft Supplies",
        "name": "Master Linocut & Block Printmaking Studio Kit",
        "brand": "Atelier Graphic",
        "price": 1499.00,
        "compare_at_price": 1850.00,
        "stock": 26,
        "badge": "New Arrival",
        "short_description": "Ergonomic cast aluminum carving handle with 5 surgical steel blades, 4x6 linoleum blocks, soft brayer roller, and water-based ink.",
        "description": "Step into the timeless art of relief printmaking. Create hand-printed greeting cards, textile stamps, and fine art prints on handmade mulberry papers.",
        "specifications": "Carver: 5 Interchangeable Precision Blades (V & U shapes)\nBrayer: 4-inch Soft Rubber Roller\nInk: Archival Black Block Printing Ink (100ml)\nSurfaces: 3 Soft-Kut Linoleum Blocks (4x6 in)",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "DIY and Craft Supplies",
        "name": "Sculptor's Polymer Oven-Bake Clay Set (24 Colors + Tools)",
        "brand": "Forma Craft",
        "price": 1099.00,
        "compare_at_price": 1350.00,
        "stock": 40,
        "badge": "Top Pick",
        "short_description": "Pliable, non-sticky modeling clay that cures durable and shatter-resistant in home kitchen ovens at 130°C.",
        "description": "Formulated for miniature sculptors, jewelry creators, and DIY crafters. Holds fine textural detail without cracking.",
        "specifications": "Quantity: 24 Vibrant Color Blocks (25g each)\nAccessories: 5 Double-Ended Sculpting Tools + Roller\nBaking: 130°C for 15-30 minutes\nSafety: Certified Non-Toxic ASTM D-4236",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 10. Artist Accessories
    {
        "category": "Artist Accessories",
        "name": "Porcelain Ceramic Flower Mixing Palette (7 Wells)",
        "brand": "ARTORA Ceramica",
        "price": 649.00,
        "compare_at_price": 799.00,
        "stock": 50,
        "badge": "Artisan Choice",
        "short_description": "Pure white glazed ceramic that never stains, beads, or discolors watercolor and gouache washes.",
        "description": "Substantial heavy weight ensures it stays firmly planted on your studio desk without sliding when loading wet brushes. Cleans effortlessly with a quick rinse.",
        "specifications": "Material: High-fired Porcelain with Gloss Glaze\nDiameter: 7 inches (18 cm)\nWells: 7 Petal Slopes + Deep Center Reservoir\nWeight: 450 grams",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Artist Accessories",
        "name": "Heavyweight Waxed Canvas Artist Studio Apron",
        "brand": "ARTORA Workshop",
        "price": 1299.00,
        "compare_at_price": 1699.00,
        "stock": 32,
        "badge": "Bestseller",
        "short_description": "Water-repellent 16oz charcoal waxed cotton canvas with reinforced brass rivets, cross-back harness, and dedicated brush pockets.",
        "description": "Takes the weight off your neck with cross-back leather-trimmed cotton straps. Protects clothes from oil, turpentine, and acrylic splatter while keeping tools at your fingertips.",
        "specifications": "Fabric: 16oz Waxed Duck Cotton Canvas\nColor: Deep Charcoal / Terracotta Accents\nPockets: 2 Chest Pencil Slots, 3 Brush Sleeves, 2 Kangaroo Pockets\nSize: Adjustable One-Size-Fits-Most",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=1000&q=80"
        ]
    },

    # 11. Art Kits and Combos
    {
        "category": "Art Kits and Combos",
        "name": "The Master Atelier Oil Painter Deluxe Chest",
        "brand": "ARTORA Signature",
        "price": 4999.00,
        "compare_at_price": 6499.00,
        "stock": 15,
        "badge": "Limited Edition",
        "short_description": "The quintessential master studio gift: 12 Artist Oil Colors, 4 Chungking Brushes, 2 Palette Knives, Linseed Medium, Turpenoid, and 2 Linen Boards in Beechwood Chest.",
        "description": "Curated for the serious oil painter. Every component has been selected for uncompromising quality and longevity, packaged in an heirloom brass-latched beechwood briefcase.",
        "specifications": "Case: Hand-stained European Beechwood\nPaints: 12 x 40ml Master Single-Pigment Oils\nMediums: 100ml Cold-Pressed Linseed Oil & Thinner\nTools: 4 Hog Brushes, 2 Flexible Knives, 2 Canvas Panels",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Art Kits and Combos",
        "name": "The Botanical Watercolorist Discovery Suite",
        "brand": "ARTORA Botanicals",
        "price": 2899.00,
        "compare_at_price": 3699.00,
        "stock": 22,
        "badge": "Bestseller",
        "short_description": "18 Honey Watercolor Pans, 2 Kolinsky Sable Brushes, 100% Cotton Hot-Pressed Block, and Ceramic Flower Palette.",
        "description": "Everything needed to capture translucent petals, botanical veins, and vibrant foliage with scientific precision and poetic grace.",
        "specifications": "Palette: 18 Fine Honey-Bound Pans in Sage Green Tin\nBrushes: Round #4 and Pointed Round #8 Kolinsky\nPaper: 300 GSM Hot-Pressed 100% Cotton Pad (15 sheets)\nPalette: 7-Well Porcelain Ceramic Dish",
        "is_featured": True,
        "is_bestseller": True,
        "images": [
            "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=1000&q=80"
        ]
    },
    {
        "category": "Art Kits and Combos",
        "name": "The Urban Sketcher's Pocket Companion Kit",
        "brand": "ARTORA Studio",
        "price": 1799.00,
        "compare_at_price": 2299.00,
        "stock": 35,
        "badge": "New Arrival",
        "short_description": "12 Half-Pan Pocket Palette, 2 Water Brushes, 3 Archival Fineliners, and A6 Lay-Flat Hardbound Watercolor Journal.",
        "description": "Slip this compact kit into your backpack and sketch cafes, historical facades, and morning commutes wherever inspiration strikes.",
        "specifications": "Tin: Pocket Metal Box with Finger Ring\nWater Brushes: Broad Flat and Detail Fine\nJournal: 200 GSM Cold Pressed Lay-Flat (80 pages)\nPens: 0.1, 0.3, and 0.5mm Waterproof Ink",
        "is_featured": False,
        "is_bestseller": False,
        "images": [
            "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1000&q=80"
        ]
    }
]

REVIEWS_SEED = [
    {
        "product_name": "Master Belgian Stretched Linen Canvas (16x20 in)",
        "rating": 5,
        "reviewer_name": "Ananya Sharma",
        "reviewer_title": "Professional Oil Painter",
        "comment": "The tooth on this Belgian linen is absolutely sublime! I did a portrait with three glaze layers and the ground held up without any sinking of the darks. Worth every single rupee."
    },
    {
        "product_name": "Master Artist Heavy Body Acrylic Set (12 x 75ml)",
        "rating": 5,
        "reviewer_name": "Devansh Roy",
        "reviewer_title": "Contemporary Muralist",
        "comment": "Incredible opacity and virtually zero color-shift when drying. The cadmium red hue and burnt umber are so rich. Will be restocking my studio with ARTORA."
    },
    {
        "product_name": "Botanical Honey Watercolor Palette (24 Half-Pans in Enamel Tin)",
        "rating": 5,
        "reviewer_name": "Kavita Raman",
        "reviewer_title": "Botanical Illustrator",
        "comment": "The honey binder makes the paint activate with just a touch of a wet brush. Beautiful granulation in the ultramarine and raw sienna. The enamel tin feels hefty and luxurious."
    },
    {
        "product_name": "Heritage Master Kolinsky Sable Brush Trio (#2, #6, #10)",
        "rating": 5,
        "reviewer_name": "Marcus Vance",
        "reviewer_title": "Fine Artist",
        "comment": "The point on the #6 is incredible. It holds enough water for an entire sky wash and then snaps back to a razor edge for telephone wires. Beautiful craftsmanship."
    },
    {
        "product_name": "The Master Atelier Oil Painter Deluxe Chest",
        "rating": 5,
        "reviewer_name": "Pooja Hegde",
        "reviewer_title": "Portrait Artist",
        "comment": "Received this as a gift from my mentor. The beechwood chest is stunning, and the paints have the buttery consistency of top European master brands."
    }
]


def seed_database():
    with app.app_context():
        print("[ARTORA Seeder] Creating database tables...")
        db.create_all()

        # 1. Create or update Default Admin & Customer accounts
        print("[ARTORA Seeder] Creating users...")
        admin = User.query.filter_by(email="admin@artora.com").first()
        if not admin:
            admin = User(
                name="Curator Admin",
                email="admin@artora.com",
                phone="+91 98765 43210",
                role="admin",
                bio="Head Curator & Studio Director at ARTORA."
            )
            admin.set_password("ArtoraAdmin2026!")
            db.session.add(admin)
            print("  Created Admin: admin@artora.com / ArtoraAdmin2026!")

        customer = User.query.filter_by(email="artist@artora.com").first()
        if not customer:
            customer = User(
                name="Mira Kapoor",
                email="artist@artora.com",
                phone="+91 98123 45678",
                role="user",
                bio="Oil painter and mixed media enthusiast exploring Indian classical landscapes."
            )
            customer.set_password("ArtoraArtist2026!")
            db.session.add(customer)
            db.session.flush()

            # Add default address for customer
            addr = Address(
                user_id=customer.id,
                label="Studio",
                full_name="Mira Kapoor",
                phone="+91 98123 45678",
                street_address="Flat 402, Lotus Art Studios, 14th Main, Indiranagar",
                city="Bengaluru",
                state="Karnataka",
                pincode="560038",
                is_default=True
            )
            db.session.add(addr)
            print("  Created Demo Artist: artist@artora.com / ArtoraArtist2026!")

        db.session.commit()

        # 2. Seed All 11 Categories
        print("[ARTORA Seeder] Seeding 11 Product Categories...")
        category_map = {}
        for cat_info in CATEGORIES_DATA:
            cat = Category.query.filter_by(name=cat_info["name"]).first()
            if not cat:
                cat = Category(
                    name=cat_info["name"],
                    slug=slugify(cat_info["name"]),
                    tagline=cat_info.get("tagline"),
                    description=cat_info.get("description"),
                    icon_class=cat_info.get("icon_class", "fa-palette"),
                    image_url=cat_info.get("image_url"),
                    display_order=cat_info.get("display_order", 0),
                    is_featured=cat_info.get("is_featured", False)
                )
                db.session.add(cat)
                db.session.flush()
                print(f"  Added Category: {cat.name}")
            category_map[cat.name] = cat

        db.session.commit()

        # 3. Seed Products
        print("[ARTORA Seeder] Seeding Curated Products...")
        product_map = {}
        for prod_info in PRODUCTS_DATA:
            cat = category_map.get(prod_info["category"])
            if not cat:
                continue

            prod = Product.query.filter_by(name=prod_info["name"]).first()
            if not prod:
                prod = Product(
                    category_id=cat.id,
                    name=prod_info["name"],
                    slug=slugify(prod_info["name"]),
                    brand=prod_info.get("brand", "ARTORA Studio"),
                    price=prod_info["price"],
                    compare_at_price=prod_info.get("compare_at_price"),
                    stock_quantity=prod_info.get("stock", 50),
                    badge=prod_info.get("badge"),
                    short_description=prod_info.get("short_description"),
                    description=prod_info["description"],
                    specifications=prod_info.get("specifications"),
                    is_featured=prod_info.get("is_featured", False),
                    is_bestseller=prod_info.get("is_bestseller", False),
                    is_active=True
                )
                db.session.add(prod)
                db.session.flush()

                # Add images
                images = prod_info.get("images", [])
                for idx, img_url in enumerate(images):
                    p_img = ProductImage(
                        product_id=prod.id,
                        image_url=img_url,
                        alt_text=prod.name,
                        is_primary=(idx == 0),
                        display_order=idx
                    )
                    db.session.add(p_img)

                print(f"  Added Product: {prod.name} (₹{prod.price})")
            product_map[prod.name] = prod

        db.session.commit()

        # 4. Seed Reviews
        print("[ARTORA Seeder] Seeding Reviews...")
        for r_info in REVIEWS_SEED:
            prod = product_map.get(r_info["product_name"])
            if prod:
                existing_rev = Review.query.filter_by(product_id=prod.id, reviewer_name=r_info["reviewer_name"]).first()
                if not existing_rev:
                    rev = Review(
                        product_id=prod.id,
                        user_id=customer.id if customer else None,
                        rating=r_info["rating"],
                        reviewer_name=r_info["reviewer_name"],
                        reviewer_title=r_info.get("reviewer_title", "Verified Artist"),
                        comment=r_info["comment"],
                        verified_buyer=True
                    )
                    db.session.add(rev)
                    db.session.flush()
                    prod.update_rating()

        db.session.commit()
        print("[ARTORA Seeder] Database seeded successfully!")


if __name__ == '__main__':
    seed_database()
