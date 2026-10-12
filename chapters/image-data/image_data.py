from blocks import *
import math, calc, gal, real
FOV = gal.FOV
HDR = real.HDR                                                               # matrix, pixel size, and bit depth read from the DICOM headers of the real images in the guide
hsize = lambda h: h["rows"] * h["cols"] * h["allocated"] // 8 / 1e6        # uncompressed size of one image in MB

levels = lambda bits: 2 ** bits
size_b = lambda nx, ny, bits: nx * ny * (bits // 8)                          # bytes for an image of nx x ny pixels
mb = lambda b: b / 1e6
px = lambda fov, n: 10 * fov / n                                             # pixel size in mm for a field of view in cm
s_ct, s_rad, s_512 = size_b(1024, 1024, 16), size_b(2000, 2500, 16), size_b(512, 512, 16)
study = lambda n, nx=512, ny=512, bits=16: n * size_b(nx, ny, bits)

TOPIC = dict(
    id="image-data", domain=4, sub="IV.A", title="Digital images, DICOM, and PACS",
    ref=dict(aapm="TG-263", khan="", ford="19"),
    guide=[
        H("Pixels and bit depth"),
        P("A digital image is a grid of pixels, the name being a contraction of picture element. A typical CT slice has 512 × 512 or 1024 × 1024 pixels, and a radiograph about 2000 × 2500. The number of pixels is not the only thing that sets the resolution. The focal spot and the distance of the object from the detector also limit it, and more pixels cannot make up for a large focal spot or a large object-to-detector distance."),
        P("Each pixel value is stored as a binary number. Each binary digit, or bit, holds a 0 or a 1, and a byte is 8 bits. With n bits a pixel can take 2<sup>n</sup> values, which is the number of grayscale levels, called the bit depth. One bit gives only black and white. Eight bits give 256 levels, and medical images are often stored with 2 bytes per pixel, a depth of 16 bits and 65,536 levels. A 4-bit image has only 16 levels, and it hides the subtle soft-tissue differences that a medical image must show."),
        EX("Grayscale levels", STEM("Three images use different bit depths.", ["4 bits", "8 bits", "16 bits"], "Find the number of [[grayscale levels]] in each."), ["Levels = 2<sup>n</sup>"], f"{levels(4)}, {levels(8)}, and {levels(16):,} levels."),

        P(f"The HU values of a CT span 4096 HU, so n bits divide them into 2<sup>n</sup> levels of 4096 / 2<sup>n</sup> HU each. With 4 bits each level is 256 HU wide, and the 400 HU soft-tissue window holds only {400 * 16 / 4096:.1f} levels, so the soft-tissue differences fall into one or two grey levels and vanish. With 8 bits there are {400 * 256 / 4096:.0f} levels in the window, and with 12 bits one level is 1 HU. Reducing the matrix makes the pixels larger: a field of view of {FOV:.0f} mm on 64 × 64 pixels gives pixels of {FOV / 64:.1f} mm."),
        AVF("ct-bits"),
        H("Storage and compression"),
        P("The storage needed for an image is the number of pixels times the number of bytes per pixel. A 1024 × 1024 image stored with 16 bits, which is 2 bytes, needs 1024 × 1024 × 2 = 2,097,152 bytes, about 2.1 MB. A 512 × 512 image at 16 bits needs 0.52 MB, and a CT study of 200 slices needs about 105 MB. The pixel size follows from the field of view: a field of view of 50 cm across 512 pixels gives 500 mm / 512 = 0.98 mm."),
        P(f"The DICOM headers of the real images give their matrix, pixel size, and bit depth. One image needs {min(hsize(h) for h in HDR):.2f} to {max(hsize(h) for h in HDR):.0f} MB, a range of more than two orders of magnitude, from a PET slice to a radiograph."),
        TABLE(["Real image", "Matrix", "Pixel (mm)", "Bits stored", "Size (MB)"], [[h["label"], f"{h['cols']} × {h['rows']}", f"{h['pixel_mm']:.2f}", f"{h['stored']} of {h['allocated']}", f"{hsize(h):.2f}"] for h in sorted(HDR, key=lambda h: -hsize(h))]),
        P("Compression reduces the storage. It relies on the fact that neighbouring pixels are related, so that a black pixel is likely to lie next to another black pixel. Lossless compression allows the exact original image to be recovered, and it saves only a factor of about 2 or 3. Lossy compression saves a factor of 10 or more, but it cannot be reversed and may degrade the image, which can affect diagnosis. Lossy compression may therefore not be suitable for medical images. How an image is displayed also matters: the window and level, which the user controls, set the brightness and the contrast shown on the screen."),
        EX("Storage of a CT study", STEM("A CT study of 200 slices, each 512 × 512 pixels stored with 16 bits per pixel.", [], "Find the [[storage]] for one slice and for the study."), ["One slice: 512 × 512 × 2 bytes", "Study: 200 × one slice"], f"One slice is {s_512:,} bytes, which is {mb(s_512):.2f} MB. The study is {mb(study(200)):.0f} MB."),

        H("DICOM, PACS, and records"),
        P("Digital Imaging and Communications in Medicine (DICOM) is the protocol that controls how images are stored, viewed, and transferred between systems. Before the early 1980s each vendor used its own format, so systems could not connect. The American College of Radiology and the National Electrical Manufacturers Association began a standardization effort in the mid-1980s. The first standard was published in 1985, and DICOM 3.0, a NEMA standard from 1993, is still used."),
        P("DICOM-RT is an extension for radiation therapy. First published in 1996, it covers structure sets (contours), RT plans, RT doses, and RT images. The National Cancer Institute required it in all trials by 2013. A picture archiving and communications system (PACS) is not a standard like DICOM. It is a system for storing images, such as a hospital radiology PACS, and it uses DICOM to communicate with other systems."),
        P("The electronic health record (EHR) is the software and database that hold patient information such as demographics, history, medications, and imaging results. The oncology information system (OIS) is distinct from the EHR. It holds oncology-specific records and interfaces with the linacs and other treatment delivery systems. The systems with the largest share in radiation oncology are Aria (Varian) and Mosaiq (Elekta). In older language they were called record-and-verify systems, because they were first designed to record and verify the correct delivery of a treatment."),
    ],
    cards=[
        F("Pixel", "A picture element: one cell of the grid that makes a digital image."),
        F("Typical matrix sizes", "About 512 × 512 or 1024 × 1024 pixels for CT, and about 2000 × 2500 for a radiograph."),
        F("Resolution and pixel count", "More pixels cannot make up for a large focal spot or a large object-to-detector distance, which also limit the resolution."),
        F("Bit and byte", "A binary digit (bit) holds a 0 or a 1. A byte is 8 bits and holds values up to 255."),
        F("Bit depth", "With n bits a pixel has 2<sup>n</sup> grayscale levels. 8 bits give 256 levels, and 16 bits give 65,536."),
        F("Storage of an image", "Pixels × bytes per pixel. A 1024 × 1024 image at 16 bits needs about 2.1 MB."),
        F("Pixel size", "Field of view divided by the number of pixels. 50 cm across 512 pixels gives about 0.98 mm."),
        F("Lossless compression", "The exact image can be recovered, but the saving is only a factor of about 2 or 3."),
        F("Lossy compression", "Saves a factor of 10 or more but cannot be reversed, and may degrade the image, so it may not suit medical images."),
        F("Window and level", "The user-controlled brightness and contrast with which an image is displayed."),
        F("DICOM", "The protocol that controls how medical images are stored, viewed, and transferred. DICOM 3.0 has been a NEMA standard since 1993."),
        F("DICOM-RT", "An extension of DICOM for radiation therapy: structure sets, RT plans, RT doses, and RT images. First published in 1996."),
        F("PACS", "A picture archiving and communications system: a system for storing images. It uses DICOM to communicate and is not a standard itself."),
        F("EHR and OIS", "The EHR holds general patient information. The oncology information system holds oncology records and drives the linacs. Examples are Aria and Mosaiq."),
    ],
)

PROBLEMS = [
    PR("A binary digit, or bit, is:", "a quantity that holds a value of 0 or 1", ["a group of 8 binary digits", "a pixel in an image", "a unit of image contrast"],
       "A byte is 8 bits. A pixel value is stored as one or more bytes.", lvl="Easy"),
    PR("The DICOM standard governs:", "how medical images are stored, viewed, and transferred between systems", ["how a linac delivers a treatment", "the choice of reconstruction filter", "the exposure at the skin of the patient"],
       "Before DICOM each vendor used its own format. DICOM provides a common standard.", lvl="Easy"),
    PRN(STEM("An image is stored with 8 bits per pixel.", [], "How many [[grayscale levels]] can each pixel have?"), levels(8), [8.0, 16.0, 65536.0], "{:.0f}",
        f"Levels = 2<sup>n</sup> = 2<sup>8</sup> = {levels(8)}. Using n itself gives 8, and 2<sup>16</sup> is {levels(16):,}.", lvl="Moderate"),
    PRN(STEM("An image of 512 × 512 pixels is stored with 16 bits per pixel.", [], "What is the [[storage size]]?"), mb(s_512), [mb(512 * 512), mb(512 * 512 * 16), mb(512 * 512 * 4)], "{:.2f} MB",
        f"Storage = 512 × 512 × 2 bytes = {s_512:,} bytes = {mb(s_512):.2f} MB. Forgetting the 2 bytes per pixel gives {mb(512 * 512):.2f} MB, and using the 16 bits as bytes gives {mb(512 * 512 * 16):.1f} MB.", lvl="Moderate"),
    PR("Lossless compression of an image:", "allows the exact original to be recovered, with a saving of only a factor of about 2 or 3", ["discards detail to save a factor of 10 or more", "cannot be reversed", "is never used for medical images"],
       "Lossy compression saves much more but cannot be reversed. Lossless compression keeps every pixel value.", lvl="Moderate"),
    PR("An image with 4 bits per pixel is poor for medical use because it:", "has only 16 grayscale levels, which hides subtle soft-tissue differences", ["has too many pixels", "cannot be displayed on a screen", "cannot be compressed"],
       "Medical images often use 16 bits, which gives 65,536 levels.", lvl="Moderate"),
    PR("DICOM-RT extends DICOM to radiation therapy. Which of these does it include?", "Structure sets, RT plans, RT doses, and RT images", ["Only RT images", "Only the beam data of the linac", "The patient's billing records"],
       "DICOM-RT objects cover the contours, the plan, the dose, and the images.", lvl="Challenging"),
    PR("A PACS differs from DICOM in that a PACS is:", "a system for storing images, which uses DICOM to communicate", ["a standard for image formats", "a standard for dose files", "a type of detector"],
       "DICOM is a standard. A PACS is a storage system that uses the standard.", lvl="Challenging"),
    PRN(STEM("A field of view of 50 cm is reconstructed on a matrix of 512 × 512 pixels.", [], "What is the [[pixel size]]?"), px(50, 512), [500 / 256, 50 / 512, 512 / 50], "{:.2f} mm",
        f"Pixel size = 500 mm / 512 = {px(50, 512):.2f} mm. Using 50 as millimetres gives {50 / 512:.2f}, and inverting the ratio gives {512 / 50:.1f}.", lvl="Challenging"),
]

TERMS = ['bit depth', 'lossless', 'DICOM', 'PACS']

TAKE = [
    [('With n bits a pixel has 2<sup>n</sup> grayscale levels. Medical images often use 16 bits, which gives 65,536 levels.', 'bit-depth')],
    [('Storage = pixels × bytes per pixel. Lossless compression saves a factor of about 2 or 3, and lossy compression 10 or more.', 'storage-size')],
    [('DICOM is the standard for images and DICOM-RT extends it to therapy. A PACS stores images, the EHR holds the record, and the OIS drives the treatment.', 'informatics-map')],
]


# ---------------------------------------------------------------- sorting, typed, and tap-the-figure questions
PROBLEMS += [
]
INLINE = {0: [1, 3], 1: [4], 2: [2, 7, 8]}
