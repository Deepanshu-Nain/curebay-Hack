# ============================================================
# data/diseases_kb.py — CureBay Disease Knowledge Base
# ============================================================
# Covers the most common health conditions in rural India:
# infectious, waterborne, vector-borne, respiratory, maternal,
# paediatric, NCDs, skin conditions, and nutritional deficiencies.
# Each entry is structured for high-quality RAG retrieval.
# Sources: WHO, ICMR, MOHFW India, PubMed rural India studies.
# ============================================================

DISEASE_KNOWLEDGE_BASE = [

    # ══════════════════════════════════════════════════════════
    # VECTOR-BORNE DISEASES
    # ══════════════════════════════════════════════════════════

    {
        "id": "malaria_plasmodium_falciparum",
        "name": "Malaria (Plasmodium falciparum — Severe)",
        "category": "Vector-borne",
        "icd10": "B50",
        "content": """
Disease: Malaria caused by Plasmodium falciparum (severe form).
Symptoms: High fever (often spiking 39–41°C with chills and rigors), severe headache, 
muscle aches, nausea and vomiting, fatigue, confusion or altered consciousness (cerebral 
malaria), jaundice, dark/cola-coloured urine (blackwater fever), rapid breathing, 
pallor due to anaemia, splenomegaly in chronic cases.
Onset: Usually 7–14 days after mosquito bite. Fever pattern may be irregular in falciparum.
Risk factors: Living near stagnant water, marshy areas, post-monsoon season (July–November), 
Odisha, Jharkhand, Chhattisgarh, northeastern India are high-endemic zones.
Complications: Cerebral malaria, severe anaemia, respiratory distress, acute renal failure, 
hypoglycaemia, death if untreated.
Triage / Risk Level: EMERGENCY if confusion, seizures, breathing difficulty, or jaundice present. 
URGENT if high fever with chills in malaria-endemic zone.
Diagnosis confirmation: Rapid Diagnostic Test (RDT) for malaria antigen, thick/thin blood smear.
Treatment: Artemisinin-combination therapy (ACT) per NVBDCP guidelines — Artesunate + 
Amodiaquine or Artemether-Lumefantrine. Severe cases: IV Artesunate + hospital admission.
Next steps: Immediate referral to PHC/CHC for RDT. If RDT positive for Pf, treat with ACT 
and monitor for danger signs. Admit if any danger sign present.
Prevention: Insecticide-treated bed nets (ITBNs), indoor residual spraying, elimination of 
breeding sites (stagnant water).
""",
        "tags": ["fever", "malaria", "chills", "headache", "vector-borne", "mosquito"],
    },

    {
        "id": "malaria_vivax",
        "name": "Malaria (Plasmodium vivax)",
        "category": "Vector-borne",
        "icd10": "B51",
        "content": """
Disease: Malaria caused by Plasmodium vivax (commonest species in India, ~50% of cases).
Symptoms: Classic 48-hour fever cycle (tertian malaria) — cold stage (shivering), hot stage 
(high fever 40°C+, headache), sweating stage (drenching sweats, fever breaks). Between attacks 
patient may feel relatively well. Anaemia, enlarged spleen.
Onset: 12–18 days incubation. Relapses possible months/years later due to liver hypnozoites.
Risk factors: Rural and peri-urban areas throughout India, all seasons but peaks post-monsoon.
Triage / Risk Level: URGENT. Rarely fatal but causes significant morbidity. Refer for diagnosis.
Diagnosis: Malaria RDT (P. vivax-specific), blood smear.
Treatment: Chloroquine (3 days) + Primaquine (14 days for radical cure to clear liver stage). 
Check G6PD status before giving Primaquine.
Next steps: Refer for RDT and blood smear. If confirmed, initiate chloroquine. Explain radical 
cure importance to prevent relapse.
""",
        "tags": ["fever", "malaria", "chills", "periodic fever", "vivax"],
    },

    {
        "id": "dengue_fever",
        "name": "Dengue Fever",
        "category": "Vector-borne",
        "icd10": "A90",
        "content": """
Disease: Dengue — viral infection spread by Aedes aegypti mosquito (daytime biter).
Symptoms: Sudden high fever (39–40°C), severe headache, retro-orbital pain (pain behind eyes), 
severe joint and muscle pain ('breakbone fever'), skin rash (maculopapular, appears day 3–5), 
nausea, vomiting, mild bleeding (gum bleed, nosebleed). Severe dengue: bleeding, plasma leakage, 
low BP, abdominal pain, vomiting blood, black tarry stools.
Warning signs of severe dengue: Abdominal pain or tenderness, persistent vomiting, 
rapid breathing, bleeding gums/nose, fatigue/restlessness, liver enlargement >2cm, 
rising haematocrit with rapid drop in platelets.
Triage: EMERGENCY if warning signs of severe dengue. URGENT for all suspected dengue cases.
Diagnosis: NS1 antigen test (days 1–5), IgM/IgG serology (after day 5), CBC for 
thrombocytopaenia (platelet drop).
Treatment: No specific antiviral. Supportive care — paracetamol for fever (NOT aspirin/ibuprofen), 
adequate oral hydration. IV fluids for severe cases. Hospital admission for severe dengue.
Next steps: Immediate referral. Monitor platelet count. Avoid NSAIDs. Fluid monitoring.
Prevention: Eliminate Aedes breeding sites (flower pots, tyres, stored water containers), 
use mosquito repellents, wear full-sleeve clothing.
""",
        "tags": ["fever", "dengue", "rash", "joint pain", "headache", "mosquito", "platelet"],
    },

    {
        "id": "chikungunya",
        "name": "Chikungunya",
        "category": "Vector-borne",
        "icd10": "A92.0",
        "content": """
Disease: Chikungunya — arbovirus spread by Aedes mosquito.
Symptoms: Sudden onset high fever, severe symmetrical joint pain (arthralgia) especially in 
wrists, ankles, knees — often debilitating, maculopapular rash, headache, muscle pain. 
Joint pain may persist for months (post-chikungunya arthritis).
Triage / Risk Level: URGENT. Refer for confirmation. NORMAL with supportive care if confirmed mild.
Diagnosis: Clinical (joint pain + fever + rash in endemic area during outbreak), PCR or serology.
Treatment: Supportive — paracetamol, NSAIDs (after dengue ruled out), rest, hydration.
Next steps: Refer if severe joint pain or in elderly/immunocompromised. Symptom management at home 
if mild.
""",
        "tags": ["fever", "joint pain", "arthralgia", "rash", "chikungunya", "mosquito"],
    },

    {
        "id": "kala_azar",
        "name": "Kala-Azar (Visceral Leishmaniasis)",
        "category": "Vector-borne",
        "icd10": "B55.0",
        "content": """
Disease: Kala-Azar / Visceral Leishmaniasis — parasitic infection by Leishmania donovani, 
spread by sandfly (Phlebotomus argentipes). Endemic in Bihar, Jharkhand, West Bengal, eastern UP.
Symptoms: Prolonged irregular fever (weeks to months), massive splenomegaly and hepatomegaly 
(very large spleen/liver), progressive weight loss, extreme weakness, severe anaemia, 
skin darkening (kala-azar = black sickness in Hindi), wasting.
Triage / Risk Level: URGENT to EMERGENCY. National Elimination Programme — all cases must be 
reported and treated.
Diagnosis: rK39 rapid test (high sensitivity in India), bone marrow/spleen aspirate in doubt.
Treatment: Government program provides free treatment — Liposomal Amphotericin B (single dose 
IV) is first-line under NVBDCP. Do not delay referral.
Next steps: Immediate referral to designated Kala-Azar treatment centre. Notify district health 
officer (mandatory).
""",
        "tags": ["fever", "splenomegaly", "anaemia", "kala azar", "leishmania", "Bihar", "Jharkhand"],
    },

    {
        "id": "japanese_encephalitis",
        "name": "Japanese Encephalitis (JE)",
        "category": "Vector-borne",
        "icd10": "A83.0",
        "content": """
Disease: Japanese Encephalitis — viral brain infection spread by Culex mosquitoes (night biters). 
Endemic in rice-growing regions of Assam, UP, Bihar, West Bengal, AP, Tamil Nadu, Karnataka.
Symptoms: Acute onset high fever, severe headache, neck stiffness (meningismus), altered 
consciousness progressing rapidly — confusion, disorientation, seizures, coma. Flaccid 
paralysis in some cases. Children <15 years most affected. Case fatality rate 20–30%, 
50% of survivors have permanent neurological sequelae.
Triage / Risk Level: EMERGENCY — all suspected JE cases require immediate hospital admission.
Diagnosis: IgM ELISA in CSF or serum. Clinical: acute fever + altered mental status + 
seizures in endemic area during monsoon/post-monsoon season.
Treatment: No specific antiviral. Supportive care — airway management, seizure control 
(IV Diazepam then Phenytoin), reduce cerebral oedema (IV Mannitol), IV fluids.
Hospital admission (ICU if available).
Next steps: Immediate emergency referral. Protect airway. Control seizures if available. 
Do not delay transport. Notify district surveillance officer (notifiable disease).
Prevention: JE vaccine (SA 14-14-2 live attenuated) included in NIS at 9 months and 
16–24 months. Mosquito control. Avoid outdoor activity at dusk/night.
""",
        "tags": ["encephalitis", "fever", "seizures", "confusion", "coma", "mosquito", "brain", "emergency"],
    },

    {
        "id": "filariasis",
        "name": "Lymphatic Filariasis (Elephantiasis)",
        "category": "Vector-borne",
        "icd10": "B74",
        "content": """
Disease: Lymphatic Filariasis — chronic parasitic infection by Wuchereria bancrofti, 
spread by Culex mosquitoes. Endemic in Bihar, UP, Odisha, Jharkhand, AP, Tamil Nadu, Kerala.
Symptoms: Acute episodes: recurrent fever, lymphangitis (painful red streaks along limbs), 
lymphadenitis (swollen painful lymph nodes), scrotal swelling. 
Chronic (years later): lymphoedema (progressive swelling of legs, arms), elephantiasis 
(massive swelling with thickened skin), hydrocele (scrotal swelling — commonest in endemic 
areas, affects up to 40% adult males in hyperendemic zones), chyluria (milky urine).
Triage: URGENT for acute attacks with fever. NORMAL for chronic management with hygiene.
Diagnosis: Peripheral blood smear (nocturnal — microfilariae appear at night), ICT 
card test (filarial antigen), clinical examination.
Treatment: MDA (Mass Drug Administration) — annual single dose DEC + Albendazole under 
National Filaria Control Programme (free). Acute episodes: Antibiotics for secondary 
infection, elevation, analgesics. Hydrocele: surgical hydrocelectomy referral.
Chronic lymphoedema: daily limb washing, elevation, exercise, skin care, compression.
Next steps: Ensure MDA compliance in endemic areas. Refer hydrocele for surgery. 
Teach limb hygiene for lymphoedema management. Counsel that early treatment prevents disability.
""",
        "tags": ["swelling", "elephantiasis", "filariasis", "lymphoedema", "hydrocele", "mosquito"],
    },

    # ══════════════════════════════════════════════════════════
    # WATERBORNE / GASTROINTESTINAL
    # ══════════════════════════════════════════════════════════

    {
        "id": "typhoid_fever",
        "name": "Typhoid Fever (Enteric Fever)",
        "category": "Waterborne/Foodborne",
        "icd10": "A01.0",
        "content": """
Disease: Typhoid — caused by Salmonella typhi. Spread through contaminated water and food.
Symptoms: Gradually rising fever (stepladder pattern) reaching 39–40°C by week 2, headache, 
malaise, anorexia, coated tongue, rose spots on abdomen (faint pink spots, rare but 
pathognomonic), relative bradycardia (pulse slower than expected for fever), 
constipation (early) or diarrhoea (late), splenomegaly. 
Complications: Intestinal perforation (sudden severe abdominal pain — EMERGENCY), 
intestinal haemorrhage, encephalopathy, hepatitis.
Triage: EMERGENCY if abdominal rigidity or perforation suspected. URGENT for confirmed/suspected typhoid.
Diagnosis: Widal test (limited sensitivity), blood culture (gold standard), Typhidot (IgM), 
Typhifast rapid test.
Treatment: Ceftriaxone IV or Azithromycin oral (fluoroquinolone resistance common in India). 
Course: 10–14 days.
Next steps: Refer to PHC/CHC for blood culture and antibiotics. Food handlers should be tested. 
Safe water and sanitation counselling. Vaccination (Typhoid conjugate vaccine) for contacts.
""",
        "tags": ["fever", "typhoid", "enteric fever", "abdominal pain", "stepladder fever"],
    },

    {
        "id": "cholera",
        "name": "Cholera",
        "category": "Waterborne",
        "icd10": "A00",
        "content": """
Disease: Cholera — caused by Vibrio cholerae. Spreads via contaminated water/food, poor sanitation.
Symptoms: Sudden onset of profuse watery diarrhoea (rice-water stools — characteristic 
pale, cloudy, voluminous), vomiting, rapid severe dehydration leading to sunken eyes, 
dry mouth, decreased skin turgor, muscle cramps (leg cramps), weak/absent pulse, 
low BP, shock. Can cause death within hours if untreated.
Triage / Risk Level: EMERGENCY — rapid dehydration is life-threatening.
Diagnosis: Clinical in outbreak setting. Stool culture/RDT confirms.
Treatment: Immediate oral rehydration solution (ORS) — large volumes. Zinc supplement. 
IV fluids (Ringer's lactate) for severe dehydration or vomiting. Doxycycline single dose 
or Azithromycin (children) reduces duration. Report outbreak immediately.
Next steps: Aggressive oral/IV rehydration — start immediately without waiting. Urgent referral. 
Notify health authorities (cholera is notifiable disease). Safe water and hygiene education.
Prevention: Safe water (boiling, chlorination), hand washing with soap, food hygiene.
""",
        "tags": ["diarrhoea", "vomiting", "dehydration", "cholera", "rice water stool", "waterborne"],
    },

    {
        "id": "acute_diarrhoea",
        "name": "Acute Diarrhoea / Gastroenteritis",
        "category": "Waterborne/Gastrointestinal",
        "icd10": "A09",
        "content": """
Disease: Acute diarrhoea — caused by multiple pathogens (rotavirus, E.coli, Shigella, Cryptosporidium).
Leading cause of under-5 mortality in India.
Symptoms: 3+ loose/liquid stools per day, abdominal cramps, nausea, vomiting, low-grade fever. 
Assess for dehydration: sunken eyes, dry mouth, no tears, decreased skin turgor, reduced urine.
Danger signs: Blood in stool (dysentery), no urine >8 hours, altered consciousness, 
unable to drink, high fever.
Triage: EMERGENCY if severe dehydration or danger signs. URGENT if moderate dehydration 
or blood in stool. NORMAL if mild diarrhoea with good oral intake.
Dehydration assessment using IMCI:
  - No dehydration: alert, drinks normally, normal skin turgor → ORS at home
  - Some dehydration: restless, thirsty, reduced skin turgor → ORS at PHC  
  - Severe dehydration: lethargic/unconscious, unable to drink → IV fluids immediately
Treatment: ORS (75 mmol/L WHO formula) — 200–400 mL after each loose stool. Zinc 20mg/day 
for 14 days (children). Continue breastfeeding. No anti-diarrhoeal drugs in children.
Next steps: Prepare and give ORS. If no improvement in 2 days or danger signs develop, 
refer immediately.
""",
        "tags": ["diarrhoea", "dehydration", "vomiting", "loose stool", "gastroenteritis", "ORS"],
    },

    {
        "id": "hepatitis_a",
        "name": "Hepatitis A",
        "category": "Waterborne",
        "icd10": "B15",
        "content": """
Disease: Hepatitis A — viral liver infection, faeco-oral route, contaminated water/food.
Symptoms: Prodrome (fever, fatigue, loss of appetite, nausea, vomiting, dark urine for 1–2 weeks) 
followed by jaundice — yellow eyes and skin (icteric jaundice), pale/clay-coloured stools, 
right upper quadrant tenderness, liver enlargement. Usually self-limiting.
Triage: URGENT — refer for liver function tests. EMERGENCY if confusion, bleeding, or fulminant hepatitis.
Diagnosis: Anti-HAV IgM, liver function tests (raised AST/ALT/bilirubin).
Treatment: Supportive — rest, high-carbohydrate/low-fat diet, adequate fluids. No alcohol. 
Avoid hepatotoxic drugs. Bed rest during acute phase.
Next steps: Refer for LFTs. Food handler restriction during illness. Household hygiene counselling. 
Report to local health authority. HAV vaccine for contacts.
""",
        "tags": ["jaundice", "hepatitis", "yellow eyes", "dark urine", "liver", "waterborne", "fatigue"],
    },

    {
        "id": "hepatitis_b",
        "name": "Hepatitis B",
        "category": "Bloodborne",
        "icd10": "B16",
        "content": """
Disease: Hepatitis B — blood-borne viral hepatitis. Routes: unprotected sex, contaminated needles, 
mother-to-child (vertical transmission), unsafe injections.
Symptoms (acute): Fatigue, anorexia, nausea, jaundice, dark urine, right upper quadrant pain, 
joint pain, rash. Chronic: often asymptomatic until cirrhosis or HCC develops.
Triage: URGENT for symptomatic acute hepatitis. Chronic HBV → regular monitoring.
Diagnosis: HBsAg test (rapid test available at PHC), HBeAg, HBV DNA.
Treatment: Acute — supportive. Chronic — Tenofovir or Entecavir (indicated based on viral load/ALT). 
Refer to gastroenterologist/hepatologist.
Prevention: Universal infant vaccination (Hep B vaccine 3-dose series included in NIS). 
Safe injection practices. Voluntary counselling and testing.
Next steps: Refer for HBsAg testing. Screen household contacts. Offer vaccination to unvaccinated contacts.
""",
        "tags": ["jaundice", "hepatitis B", "liver", "fatigue", "HBsAg", "bloodborne"],
    },

    {
        "id": "leptospirosis",
        "name": "Leptospirosis",
        "category": "Waterborne / Zoonotic",
        "icd10": "A27",
        "content": """
Disease: Leptospirosis — bacterial infection (Leptospira spirochetes). Spread via contact 
with water contaminated by urine of infected animals (rats, cattle, dogs). Major outbreaks 
post-flood in Kerala, Gujarat, Maharashtra, Karnataka.
Symptoms: Biphasic illness.
Phase 1 (septicaemic, 5–7 days): Sudden high fever with chills, severe headache, 
severe myalgia (especially calves — characteristic), conjunctival suffusion (red eyes 
without discharge — pathognomonic), nausea, vomiting, diarrhoea.
Phase 2 (immune, can be severe): Weil's disease — jaundice, renal failure (dark urine, 
oliguria), bleeding tendency, pulmonary haemorrhage (coughing blood — EMERGENCY).
Triage: EMERGENCY if jaundice + renal failure + bleeding (Weil's disease). URGENT for 
all suspected cases post-flood exposure.
Diagnosis: Clinical suspicion in post-flood setting + occupational risk (farmers, sewer workers). 
IgM ELISA (available at district level), MAT (gold standard).
Treatment: Mild: oral Doxycycline 100mg BD for 7 days. Severe: IV Penicillin G or IV 
Ceftriaxone + ICU management for organ failure.
Next steps: Refer for blood tests. Start Doxycycline if clinically suspected. 
Chemoprophylaxis: Doxycycline 200mg weekly during flood season for high-risk workers.
Prevention: Avoid wading through flood water, wear protective footwear, rodent control.
""",
        "tags": ["fever", "leptospirosis", "flood", "jaundice", "muscle pain", "red eyes", "rat", "waterborne"],
    },

    # ══════════════════════════════════════════════════════════
    # RESPIRATORY
    # ══════════════════════════════════════════════════════════

    {
        "id": "tuberculosis_pulmonary",
        "name": "Pulmonary Tuberculosis (TB)",
        "category": "Respiratory/Infectious",
        "icd10": "A15",
        "content": """
Disease: Pulmonary TB — caused by Mycobacterium tuberculosis. Airborne transmission. 
India accounts for ~26% of global TB burden.
Symptoms: Cough for 2+ weeks (most important symptom — TB must be ruled out), 
blood-tinged sputum (haemoptysis), unexplained weight loss (>10% body weight), 
evening/night fever with night sweats, loss of appetite (anorexia), fatigue, 
chest pain, breathlessness. In children: prolonged fever, not gaining weight, 
close contact with known TB case.
Extra-pulmonary TB: Swollen lymph nodes (especially neck), pleural effusion, 
abdominal TB, TB meningitis (headache + fever + neck stiffness), bone/joint TB.
Triage: URGENT — refer for sputum test within same day.
Diagnosis: CBNAAT/GeneXpert (preferred, detects drug resistance), sputum smear microscopy, 
chest X-ray, FNAC for lymph node. Nikshay portal registration mandatory.
Treatment: Under RNTCP/NTEP — free drugs provided at Designated Microscopy Centres (DMC) 
and PHCs. DS-TB: 2HRZE/4HR (6 months). DR-TB: longer regimens. Directly Observed Treatment 
(DOT) recommended.
Next steps: Refer to DMC/PHC for sputum testing. If confirmed, register on Nikshay, initiate 
DOTS. Screen household contacts. Patient must complete full treatment to prevent drug resistance.
Isolation advice: Separate sleeping area, cover mouth/nose when coughing, ensure ventilation.
""",
        "tags": ["cough", "TB", "tuberculosis", "haemoptysis", "weight loss", "night sweats", "respiratory"],
    },

    {
        "id": "pneumonia_community_acquired",
        "name": "Community-Acquired Pneumonia",
        "category": "Respiratory",
        "icd10": "J18",
        "content": """
Disease: Pneumonia — infection of lung parenchyma (Streptococcus pneumoniae commonest in adults).
Leading killer of children under 5 in India.
Symptoms: Fever, productive cough (yellow/green/rust-coloured sputum), chest pain worsening 
with breathing (pleuritic chest pain), breathlessness, fast breathing, crackles on auscultation, 
decreased breath sounds, dullness on percussion.
IMCI Fast Breathing cut-offs (tachypnoea):
  - < 2 months: ≥ 60 breaths/min
  - 2–11 months: ≥ 50 breaths/min  
  - 1–5 years: ≥ 40 breaths/min
  - > 5 years: ≥ 30 breaths/min
Danger signs in children: Chest in-drawing, stridor, grunting, cyanosis, unable to drink/feed,
convulsions, altered consciousness.
Triage: EMERGENCY if SpO2 < 90%, cyanosis, respiratory distress, shock. URGENT for confirmed 
pneumonia in children/elderly/immunocompromised. NORMAL for mild community-acquired pneumonia 
in healthy adults.
Diagnosis: Chest X-ray (consolidation), sputum culture, blood culture.
Treatment: Amoxicillin (first-line) or Amoxicillin-Clavulanate for moderate. Azithromycin 
for atypical. Severe: IV Ampicillin + Gentamicin (children), IV Ceftriaxone (adults).
Oxygen therapy for SpO2 < 94%.
Next steps: Count respiratory rate. Check SpO2. If danger signs or severe pneumonia — immediate 
referral with oxygen. For non-severe: oral amoxicillin + follow-up in 2 days.
""",
        "tags": ["pneumonia", "cough", "fever", "breathlessness", "chest pain", "fast breathing", "respiratory"],
    },

    {
        "id": "acute_respiratory_infection_upper",
        "name": "Upper Respiratory Tract Infection (URTI) / Common Cold",
        "category": "Respiratory",
        "icd10": "J06",
        "content": """
Disease: URTI — viral infection of upper airways (rhinovirus, adenovirus, influenza). 
Commonest reason for health worker visits.
Symptoms: Runny/blocked nose, sneezing, sore throat, mild fever (< 38.5°C), mild cough, 
headache, fatigue. Usually self-limiting in 7–10 days.
Triage: NORMAL in most cases. URGENT if high fever >39°C, severe sore throat (may be 
streptococcal pharyngitis), earache, or symptoms > 10 days (may indicate bacterial 
superinfection like sinusitis, otitis media).
Treatment: Symptomatic — paracetamol, adequate rest, fluids, steam inhalation, honey + 
ginger for sore throat (traditional remedy with mild evidence). No antibiotics for viral URTI.
Next steps: Reassurance and home care. Return if no improvement in 7 days, fever >39°C, 
difficulty breathing, or ear pain develops.
""",
        "tags": ["cold", "cough", "runny nose", "sore throat", "fever", "URTI", "flu"],
    },

    {
        "id": "asthma",
        "name": "Bronchial Asthma",
        "category": "Respiratory/Chronic",
        "icd10": "J45",
        "content": """
Disease: Asthma — chronic inflammatory airway disease causing reversible airflow obstruction. 
Prevalence ~2.5% in India, higher in rural areas due to biomass fuel exposure, occupational 
dust, outdoor pollution.
Symptoms: Episodic wheezing (high-pitched whistling sound during breathing), breathlessness, 
chest tightness, cough (often worse at night/early morning). Triggers: dust, smoke, pollen, 
cold air, infections, exercise, stress.
Acute severe asthma (status asthmaticus): Unable to speak in full sentences, SpO2 < 92%, 
accessory muscle use, paradoxical breathing — EMERGENCY.
Triage: EMERGENCY if severe attack. URGENT if acute exacerbation. NORMAL for stable asthma on treatment.
Diagnosis: Clinical + spirometry (reversibility test), peak flow meter.
Treatment: Short-acting beta-2 agonist (Salbutamol inhaler) for acute relief. Inhaled 
corticosteroid (Budesonide) for maintenance. Avoid triggers. For severe attack: nebulised 
Salbutamol + Ipratropium, systemic steroids, IV Magnesium sulphate, oxygen.
Next steps: For acute attack — give Salbutamol inhaler (2–4 puffs) immediately. 
If no improvement in 20 min, refer urgently. Educate on proper inhaler technique.
""",
        "tags": ["wheezing", "asthma", "breathlessness", "chest tightness", "inhaler", "respiratory"],
    },

    # ══════════════════════════════════════════════════════════
    # SKIN CONDITIONS
    # ══════════════════════════════════════════════════════════

    {
        "id": "scabies",
        "name": "Scabies",
        "category": "Skin / Parasitic",
        "icd10": "B86",
        "content": """
Disease: Scabies — highly contagious skin infestation by Sarcoptes scabiei mite. 
Very common in rural India, especially in crowded households and among children.
Symptoms: Intense itching — classically worse at night. Burrows (thin grey wavy lines) 
in web spaces between fingers, wrists, elbows, armpits, waist, buttocks, genitals. 
Small red papules, vesicles. In infants: may affect palms, soles, face, scalp. 
Crusted/Norwegian scabies in immunocompromised — thick crusty patches, highly infectious.
Triage: NORMAL in most cases. Treat all household contacts simultaneously.
Diagnosis: Clinical examination — characteristic distribution and intense nocturnal itching.
Treatment: Permethrin 5% cream — apply from neck down to toes, leave 8–14 hours, wash off. 
Repeat after 1 week. Alternative: Benzyl Benzoate 25% lotion. 
Oral Ivermectin (200 mcg/kg) for crusted scabies or mass treatment in outbreaks. 
Wash all clothing and bedding in hot water.
Next steps: Treat all household contacts same day (even if asymptomatic). Counsel on hygiene. 
Antihistamines for itch relief. Calamine lotion for symptomatic relief.
""",
        "tags": ["itching", "scabies", "rash", "skin", "mite", "nocturnal itching", "burrows"],
    },

    {
        "id": "fungal_skin_infection",
        "name": "Dermatophytosis (Ringworm / Tinea)",
        "category": "Skin / Fungal",
        "icd10": "B35",
        "content": """
Disease: Tinea — superficial fungal infection of skin (Trichophyton, Microsporum species). 
Very prevalent in tropical, humid India. Spread by direct contact, sharing clothes/towels.
Types: Tinea corporis (body — ringworm: circular scaly patch with raised edge), 
Tinea cruris (groin — 'jock itch': itchy red rash in groin folds), 
Tinea capitis (scalp: scaly patches, hair loss in children), 
Tinea pedis (foot — athlete's foot: scaling, maceration between toes), 
Tinea unguium/onychomycosis (nails: thickened, discoloured, brittle).
Symptoms: Ring-shaped lesions with clear centre and raised, scaly, red, itchy border. 
Active edge is most prominent. Itching common.
Triage: NORMAL. Chronic/extensive cases may need systemic treatment.
Diagnosis: Clinical appearance; Wood's lamp (Tinea capitis); KOH microscopy.
Treatment: Topical antifungals — Clotrimazole, Miconazole, or Terbinafine cream for 2–4 weeks 
(continue 1 week after clearing). Tinea capitis: oral Griseofulvin or Terbinafine. 
Severe/extensive: Oral Fluconazole or Itraconazole. Keep affected area dry.
Next steps: Advise to keep skin dry, avoid sharing personal items. Treat at home with topical 
antifungal. Refer if no improvement in 2 weeks or extensive involvement.
""",
        "tags": ["ringworm", "tinea", "fungal", "skin", "itching", "rash", "scaly"],
    },

    {
        "id": "infected_wound",
        "name": "Infected Wound / Cellulitis",
        "category": "Skin / Infection",
        "icd10": "L03",
        "content": """
Disease: Wound infection / Cellulitis — bacterial infection of skin and subcutaneous tissue 
(Staphylococcus aureus, Streptococcus pyogenes). Common after cuts, bites, abrasions in 
agricultural workers.
Symptoms: Redness (erythema), swelling (oedema), warmth, tenderness around wound. 
Discharge (pus for abscess). Streaking redness spreading from wound (lymphangitis — 
red lines = bacteria spreading through lymphatics — serious sign). Fever, chills in systemic infection.
Danger signs: Spreading cellulitis, red streaks, fever >38.5°C, wound over joint, 
bite wound (human/animal), gangrenous/black tissue, necrotising fasciitis (extremely painful, 
rapidly spreading, crepitus = air under skin).
Triage: EMERGENCY for necrotising fasciitis, gas gangrene, spreading infection with systemic signs. 
URGENT for lymphangitis, fever with wound infection, animal bites. NORMAL for localised wound.
Tetanus risk: All puncture wounds, soil-contaminated wounds, animal bites — assess tetanus 
immunisation status; give Tetanus Toxoid (TT) booster if not vaccinated in 5 years.
Treatment: Wound cleaning (saline/water irrigation). Topical antiseptic (Povidone-Iodine). 
Oral antibiotics: Amoxicillin-Clavulanate or Cloxacillin (for Staph). 
Abscess: Incision and drainage. IV antibiotics for severe cellulitis.
Next steps: Clean wound. Give TT if needed. Oral antibiotics for 5–7 days. Refer if red streaks, 
fever, or not improving in 48 hours.
""",
        "tags": ["wound", "infection", "cellulitis", "pus", "redness", "swelling", "skin"],
    },

    {
        "id": "leprosy",
        "name": "Leprosy (Hansen's Disease)",
        "category": "Skin / Infectious",
        "icd10": "A30",
        "content": """
Disease: Leprosy — caused by Mycobacterium leprae. Chronic infection affecting skin and 
peripheral nerves. India had high burden; being eliminated but cases still occur.
Symptoms: Hypopigmented or reddish patches on skin with loss of sensation (anaesthetic patches), 
thickened skin, peripheral nerve thickening (ulnar, common peroneal, median, radial nerves), 
muscle weakness/wasting, deformity of hands/feet/face. Painless wounds or burns (due to 
sensory loss). Clawhand, footdrop.
Types: Paucibacillary (1–5 lesions, skin smear negative) vs Multibacillary (>5 lesions, smear positive).
Triage: URGENT — not a medical emergency but requires urgent referral for MDT treatment. 
Do not delay; undetected leprosy leads to permanent disability.
Diagnosis: Skin slit smear, skin biopsy. Clinical diagnosis sufficient for treatment initiation.
Treatment: Multi-Drug Therapy (MDT) — free under NLEP. PB-MDT: 6 months. MB-MDT: 12 months. 
Rifampicin + Dapsone (PB) + Clofazimine (MB).
Lepra reactions: Type 1 (reversal reaction) and Type 2 (ENL) — require steroids and urgent referral.
Next steps: Refer to leprosy clinic/PHC. Counsel on MDT (free treatment). Educate patient 
that leprosy is curable and transmission is low. Reduce stigma.
""",
        "tags": ["leprosy", "skin patch", "numbness", "nerve", "anaesthetic patch", "Hansen"],
    },

    # ══════════════════════════════════════════════════════════
    # NON-COMMUNICABLE DISEASES
    # ══════════════════════════════════════════════════════════

    {
        "id": "diabetes_mellitus_type2",
        "name": "Type 2 Diabetes Mellitus",
        "category": "NCD / Metabolic",
        "icd10": "E11",
        "content": """
Disease: Type 2 Diabetes — chronic metabolic disorder with insulin resistance and relative 
insulin deficiency. Rapidly rising in rural India (estimated 8–10% rural adults affected).
Symptoms: Polyuria (frequent urination), polydipsia (excessive thirst), polyphagia 
(increased hunger), unexplained weight loss (in poorly controlled), fatigue, blurred vision, 
slow-healing wounds, recurrent infections (skin, urinary tract, candida), tingling/numbness 
in feet (peripheral neuropathy), erectile dysfunction.
Often asymptomatic for years — discovered on screening.
Acute complications: Hyperglycaemic hyperosmolar state (extreme thirst, confusion, dry skin) — 
EMERGENCY. Hypoglycaemia (sweating, trembling, confusion, loss of consciousness in patient 
on insulin/sulphonylureas) — EMERGENCY.
Chronic complications: Diabetic foot (ulcers, infections, gangrene), nephropathy (kidney failure), 
retinopathy (blindness), cardiovascular disease.
Screening criteria: Fasting blood glucose ≥ 126 mg/dL OR random ≥ 200 mg/dL with symptoms 
OR HbA1c ≥ 6.5%.
Triage: EMERGENCY for hypoglycaemia or hyperglycaemic crisis. URGENT if new diagnosis or 
uncontrolled diabetes with complications. NORMAL for routine monitoring of controlled diabetes.
Treatment: Lifestyle (diet + exercise), Metformin (first-line oral), sulphonylureas, 
Insulin (required in type 1 and advanced type 2). NPCDCS provides free medicines at PHC.
Next steps: Glucometer finger-prick test. Refer to PHC/CHC for HbA1c, lipid profile, renal 
function. Foot examination at every visit. Annual dilated eye exam.
""",
        "tags": ["diabetes", "sugar", "polyuria", "thirst", "glucose", "NCD", "metabolic"],
    },

    {
        "id": "hypertension",
        "name": "Hypertension (High Blood Pressure)",
        "category": "NCD / Cardiovascular",
        "icd10": "I10",
        "content": """
Disease: Hypertension — BP ≥ 140/90 mmHg on 2 separate occasions. Leading cause of 
cardiovascular mortality in India. Massively under-diagnosed in rural areas.
Symptoms: Usually asymptomatic ('silent killer'). Symptoms when severe or with complications: 
headache (occipital — back of head), dizziness, blurred vision, nosebleed, chest pain, 
shortness of breath.
Hypertensive crisis (BP > 180/120): Headache, visual disturbance, confusion, chest pain, 
signs of end-organ damage — EMERGENCY.
Classification (JNC 8 / ISH 2020):
  Normal: < 120/80
  Elevated: 120–129/< 80
  Stage 1 HTN: 130–139/80–89
  Stage 2 HTN: ≥ 140/90
  Hypertensive crisis: > 180/120
Diagnosis: Sphygmomanometer BP measurement (properly, seated, 2 readings, 5 min apart).
Treatment: Lifestyle — salt restriction (< 5g/day), weight loss, exercise, stop smoking, 
limit alcohol. Medications: Amlodipine (calcium channel blocker), Enalapril/Lisinopril (ACE 
inhibitor), Thiazide diuretic. Under NPCDCS, medicines available free at PHC.
Next steps: Measure BP accurately. If BP > 180/120 with symptoms → immediate referral. 
If newly diagnosed, refer to PHC for workup and initiate lifestyle changes. 
Counsel on medication adherence — explain hypertension requires lifelong treatment.
""",
        "tags": ["hypertension", "blood pressure", "headache", "BP", "cardiovascular", "NCD"],
    },

    {
        "id": "heart_attack_mi",
        "name": "Acute Myocardial Infarction (Heart Attack)",
        "category": "Cardiovascular / Emergency",
        "icd10": "I21",
        "content": """
Disease: Acute MI — blockage of coronary artery causing heart muscle death.
Symptoms: Severe central chest pain — crushing, squeezing, pressure-like, radiating to left arm, 
jaw, neck, back. Sweating (diaphoresis), nausea, vomiting, dizziness, breathlessness, 
sense of impending doom. May present atypically in diabetics/elderly/women: jaw pain, fatigue, 
breathlessness without chest pain.
Triage: EMERGENCY — time is muscle. Every minute of delay = more myocardium lost.
'Time to treatment' target: < 90 min from symptom onset to intervention.
Next steps (immediate — before transport):
  1. Call for ambulance immediately (108 in most states)
  2. Aspirin 300mg oral (chew, not swallow) if not contraindicated — reduces mortality
  3. Lay patient flat with head elevated 30 degrees
  4. Loosen tight clothing, reassure
  5. Do NOT give food/water
  6. Monitor pulse and consciousness
  7. Transport immediately to nearest hospital with cardiac care
Never delay transport for ECG.
""",
        "tags": ["chest pain", "heart attack", "MI", "crushing pain", "emergency", "cardiac"],
    },

    {
        "id": "stroke_cva",
        "name": "Stroke (Cerebrovascular Accident)",
        "category": "Neurological / Emergency",
        "icd10": "I64",
        "content": """
Disease: Stroke — sudden brain damage from interrupted blood supply (ischaemic) or bleeding 
(haemorrhagic). Medical emergency — brain cells die within minutes.
FAST Test — Recognition:
  F — Face drooping (asymmetrical smile, facial weakness)
  A — Arm weakness (one arm drifts down when raised)
  S — Speech difficulty (slurred, garbled, unable to speak)
  T — Time to call 108 immediately
Other symptoms: Sudden severe headache ('thunderclap' — worst of life), sudden confusion, 
visual loss (one or both eyes), sudden loss of balance, walking difficulty.
TIA (mini-stroke): Same symptoms but resolve within 24 hours — URGENT referral needed 
(high risk of major stroke within 2 days).
Triage: EMERGENCY for all suspected strokes. Time-sensitive: thrombolysis must be given 
within 4.5 hours of onset.
Next steps:
  1. Note exact time symptoms started
  2. Apply FAST test
  3. Do NOT give food/water/medicines by mouth (swallowing may be impaired)
  4. Lay in recovery position if unconscious
  5. Call 108 for immediate transport to hospital
  6. Transport to nearest stroke-capable hospital
""",
        "tags": ["stroke", "face drooping", "weakness", "speech", "emergency", "neurological", "FAST"],
    },

    # ══════════════════════════════════════════════════════════
    # MATERNAL HEALTH
    # ══════════════════════════════════════════════════════════

    {
        "id": "pre_eclampsia_eclampsia",
        "name": "Pre-eclampsia / Eclampsia",
        "category": "Maternal Health / Emergency",
        "icd10": "O14 / O15",
        "content": """
Disease: Pre-eclampsia — hypertension (BP ≥ 140/90) + proteinuria after 20 weeks gestation. 
Eclampsia = pre-eclampsia + seizures. Leading cause of maternal mortality in India.
Symptoms (pre-eclampsia): Headache (severe, frontal), visual disturbances (blurring, flashing 
lights), epigastric/right upper quadrant pain, sudden oedema (swelling face/hands/feet), 
nausea, vomiting. BP > 160/110 = severe features.
Eclampsia: Tonic-clonic seizures in pregnant/postpartum woman — EMERGENCY.
Triage: EMERGENCY for eclampsia (seizures) or severe pre-eclampsia (BP > 160/110, 
headache with hypertension, visual symptoms). URGENT for any elevated BP in pregnancy.
Next steps for eclampsia (before transport):
  1. Position: left lateral position (reduces aorto-caval compression)
  2. Protect from injury (do NOT insert anything in mouth)
  3. Ensure airway — suction if vomiting
  4. Magnesium Sulphate injection (if available and trained) — loading dose 4g IV slowly 
     or IM (4g each buttock) — prevents/stops seizures
  5. Antihypertensives if BP > 160/110: Labetalol IV or oral Nifedipine
  6. Immediate referral to FRU/district hospital
  7. Call 108 ambulance
NOTE: Only deliver at referral hospital. Magnesium sulphate is life-saving — ensure 
it is available at subcentre level.
""",
        "tags": ["pregnancy", "eclampsia", "pre-eclampsia", "seizure", "BP", "maternal", "emergency"],
    },

    {
        "id": "postpartum_haemorrhage",
        "name": "Postpartum Haemorrhage (PPH)",
        "category": "Maternal Health / Emergency",
        "icd10": "O72",
        "content": """
Disease: PPH — excessive bleeding (>500 mL vaginal delivery, >1000 mL caesarean) after 
delivery. Commonest cause of maternal mortality in India. Causes: Tone (uterine atony — 80%), 
Trauma (lacerations), Tissue (retained placenta), Thrombin (coagulopathy).
Recognition: Soaking >2 pads in 15 min, bright red bleeding, dizziness, rapid pulse, 
falling BP, pallor, cold clammy skin.
Triage: EMERGENCY — all PPH is emergency. Rapid blood loss → shock → death in minutes.
Immediate actions (ASHA/ANM):
  1. Uterine massage — bimanual compression of uterus
  2. Oxytocin 10 IU IM (if available and woman has delivered) — FIRST LINE
  3. If Oxytocin not available: Misoprostol 800 mcg sublingual
  4. Empty bladder (catheterise)
  5. IV access — 2 large bore cannulas, start Ringer's Lactate
  6. Keep patient warm
  7. Immediate referral (call 108)
  8. Apply aortic compression if severe bleeding and transport delayed
Active Management of Third Stage Labour (AMTSL) prevents PPH: Oxytocin within 1 min 
of delivery of baby + controlled cord traction + uterine massage.
""",
        "tags": ["postpartum", "PPH", "bleeding", "delivery", "maternal", "emergency", "haemorrhage"],
    },

    {
        "id": "anaemia_pregnancy",
        "name": "Anaemia in Pregnancy",
        "category": "Maternal Health / Nutritional",
        "icd10": "O99.0",
        "content": """
Disease: Anaemia in pregnancy — Hb < 11 g/dL. Affects ~50% of pregnant women in rural India. 
Causes: iron deficiency (commonest), folate/B12 deficiency, malaria, worm infestation, 
sickle cell disease, thalassemia.
Severity: Mild 10–10.9 g/dL, Moderate 7–9.9 g/dL, Severe <7 g/dL, Very severe <4 g/dL.
Symptoms: Pallor (conjunctiva, palms, tongue), fatigue, breathlessness on exertion, 
palpitations, dizziness, headache, swollen feet, reduced fetal movement (severe cases).
Risks: Preterm delivery, low birth weight, maternal death during haemorrhage, 
impaired cognitive development in child.
Triage: URGENT for severe anaemia (Hb<7) in pregnancy. NORMAL with treatment for mild/moderate.
Assessment: Check conjunctival/palm pallor (clinical screening). CBC for Hb level. 
HPLC for haemoglobinopathy screening.
Treatment: 
  - Iron Folic Acid (IFA) tablets (100mg iron + 0.5mg folic acid) daily — 
    free under PMSMA/ICDS. Take with Vitamin C, not with tea.
  - Severe anaemia: IV iron (ferric carboxymaltose) or blood transfusion
  - Treat underlying cause (malaria, worms — deworm with Albendazole in 2nd trimester)
Next steps: Register on PMSMA (Pradhan Mantri Surakshit Matritva Abhiyan) for ANC. 
Ensure IFA compliance. Dietary counselling (green leafy vegetables, jaggery, dates). 
Refer for Hb if pallor present. Urgent referral if Hb < 7 g/dL or symptomatic.
""",
        "tags": ["anaemia", "pregnancy", "pallor", "fatigue", "haemoglobin", "iron deficiency", "maternal"],
    },

    # ══════════════════════════════════════════════════════════
    # PAEDIATRIC
    # ══════════════════════════════════════════════════════════

    {
        "id": "severe_acute_malnutrition",
        "name": "Severe Acute Malnutrition (SAM)",
        "category": "Paediatric / Nutritional",
        "icd10": "E43",
        "content": """
Disease: SAM in children under 5 — defined by:
  - MUAC (Mid-Upper Arm Circumference) < 11.5 cm, OR
  - Weight-for-height Z-score < -3 SD, OR
  - Bilateral pitting oedema of nutritional origin
India has world's highest burden of child undernutrition.
Signs: Visible severe wasting (ribs visible, hollow cheeks — Marasmus), or oedema 
(swollen legs, face — Kwashiorkor), skin changes (cracking 'flaky paint dermatosis'), 
hair changes (reddish, sparse, easily pluckable), extreme weakness, apathy.
Danger signs (complicated SAM — hospital admission needed):
  - Anorexia (refuses therapeutic food)
  - Fever >38.5°C
  - Hypothermia <35.5°C
  - Respiratory distress
  - Severe dehydration
  - Convulsions
  - Altered consciousness
  - Severe anaemia
Triage: EMERGENCY if complicated SAM (danger signs). URGENT for uncomplicated SAM.
Diagnosis: MUAC tape (green >12.5cm, yellow 11.5–12.4cm, red <11.5cm). Weight/height.
Treatment: Uncomplicated SAM → Community-based management with RUTF (Ready-to-Use 
Therapeutic Food) — available at AWC/NRC. Complicated SAM → Nutrition Rehabilitation 
Centre (NRC) admission.
Next steps: MUAC measurement. Refer to NRC if complicated. Enrol in POSHAN programme. 
Breastfeeding support. Vitamin A, zinc, folic acid supplementation.
""",
        "tags": ["malnutrition", "SAM", "wasting", "MUAC", "child", "paediatric", "oedema", "kwashiorkor"],
    },

    {
        "id": "measles",
        "name": "Measles",
        "category": "Paediatric / Vaccine-Preventable",
        "icd10": "B05",
        "content": """
Disease: Measles — highly contagious viral disease (paramyxovirus). Vaccine preventable.
Still causes outbreaks in under-immunised communities in India.
Symptoms: Prodrome (3–5 days): high fever, cough, coryza (runny nose), conjunctivitis (red 
watery eyes). Koplik's spots (white spots on buccal mucosa — pathognomonic, appear before rash). 
Rash: maculopapular, starts face/hairline, spreads downward to trunk and limbs (day 3–4), 
fever worsens when rash appears.
Complications: Pneumonia (commonest cause of measles death), encephalitis, corneal ulceration 
leading to blindness, severe diarrhoea, acute otitis media, malnutrition (post-measles 
immune suppression).
Triage: URGENT — refer for Vitamin A and supportive care. EMERGENCY if pneumonia, 
encephalitis, or severe dehydration.
Treatment: Supportive — Vitamin A supplementation (200,000 IU on days 1 and 2) reduces 
severity and complications significantly. Treat complications. No specific antiviral.
Report all suspected measles cases to district health officer (notifiable disease).
Next steps: Vitamin A immediately. ORS for diarrhoea. Refer if complications present. 
Report to health authorities. Check immunisation status of contacts — catch-up vaccination.
Prevention: MR vaccine at 9 months and 15–18 months under NIS. 
""",
        "tags": ["measles", "rash", "fever", "child", "koplik spots", "vaccine", "paediatric"],
    },

    {
        "id": "chickenpox",
        "name": "Chickenpox (Varicella)",
        "category": "Paediatric / Viral",
        "icd10": "B01",
        "content": """
Disease: Chickenpox — highly contagious viral infection (Varicella-Zoster Virus). Airborne 
and contact transmission. Common in children, outbreaks in crowded settings/schools.
Symptoms: Prodrome (fever, malaise 1–2 days), then characteristic rash — starts on face/trunk, 
spreads to limbs. Rash progresses: macules → papules → vesicles (clear fluid-filled blisters 
on red base — 'dewdrop on a rose petal') → pustules → crusts. HALLMARK: Lesions in 
different stages simultaneously (unlike smallpox).
Intensely itchy. New crops appear for 3–5 days. Usually self-limiting in healthy children.
Complications: Secondary bacterial skin infection (Staph/Strep — commonest complication), 
pneumonia (adults > children), encephalitis, hepatitis. Risk groups: neonates, adults, 
immunocompromised, pregnant women.
Triage: NORMAL for uncomplicated chickenpox in healthy children. URGENT if adult, pregnant, 
immunocompromised, or complications present. EMERGENCY if encephalitis or pneumonia.
Treatment: Symptomatic — Paracetamol for fever (NOT aspirin — risk of Reye syndrome), 
Calamine lotion for itch, antihistamines. Keep nails short to prevent scratching. 
Acyclovir oral for adolescents, adults, immunocompromised — started within 24 hours of rash.
Next steps: Isolate from school/community until all lesions crusted (usually 5–7 days). 
Refer if adult, pregnant, or any complication. Counsel on hygiene to prevent secondary infection.
Prevention: Varicella vaccine (available but not yet in NIS in most states).
""",
        "tags": ["chickenpox", "varicella", "rash", "vesicles", "blisters", "itching", "child", "fever"],
    },

    {
        "id": "diphtheria",
        "name": "Diphtheria",
        "category": "Paediatric / Vaccine-Preventable",
        "icd10": "A36",
        "content": """
Disease: Diphtheria — caused by Corynebacterium diphtheriae. Resurgent in under-vaccinated 
pockets of India (outbreaks reported in Rajasthan, Gujarat, and northeastern states).
Symptoms: Sore throat, low-grade fever, swollen neck ('bull neck' — due to cervical lymphadenopathy), 
tough grey-white adherent membrane on tonsils/pharynx — HALLMARK (bleeds on attempted removal), 
difficulty breathing, stridor (if membrane extends to larynx — croup-like presentation). 
Cardiac complications: myocarditis (arrhythmias, heart failure) — 2–3 weeks after onset.
Neurological: cranial nerve palsies (nasal regurgitation, palatal paralysis).
Triage: EMERGENCY — diphtheria is life-threatening. Immediate referral required.
Airway obstruction from membrane is a direct threat to life.
Diagnosis: Clinical (membrane + bull neck in unvaccinated child). Throat swab culture.
Treatment: Diphtheria Antitoxin (DAT) — must be given ASAP. Antibiotics: Penicillin or 
Erythromycin for 14 days. Tracheostomy may be needed for airway obstruction.
Hospital admission mandatory.
Next steps: Immediate referral to hospital. Do not attempt to remove membrane. 
Ensure airway. Notify health authorities (notifiable disease). Vaccinate all contacts 
and give prophylactic antibiotics to close contacts.
Prevention: DPT/Pentavalent vaccine in NIS. Booster doses at 16–24 months and 5–6 years.
""",
        "tags": ["diphtheria", "sore throat", "membrane", "bull neck", "fever", "child", "vaccine", "emergency"],
    },

    # ══════════════════════════════════════════════════════════
    # NUTRITIONAL DEFICIENCIES
    # ══════════════════════════════════════════════════════════

    {
        "id": "iron_deficiency_anaemia",
        "name": "Iron Deficiency Anaemia",
        "category": "Nutritional Deficiency",
        "icd10": "D50",
        "content": """
Disease: Iron deficiency anaemia — commonest nutritional deficiency globally. 
India: ~53% women, ~58% children under 5 are anaemic (NFHS-5 data).
Symptoms: Pallor (inner eyelid, palms, tongue — most reliable clinical sign), 
fatigue, weakness, breathlessness on exertion, dizziness, palpitations, 
reduced concentration, cold intolerance, brittle nails, spoon-shaped nails (koilonychia), 
angular stomatitis (cracks at corners of mouth), glossitis (smooth sore tongue), 
pica (craving non-food items like clay/mud/ice — called geophagic pica).
Clinical screening: MUAC pallor (conjunctival/palmar pallor).
Diagnosis: Hb level (< 12 g/dL women, < 13 g/dL men, < 11 g/dL pregnant, < 11 g/dL children under 5). 
Peripheral blood smear (microcytic hypochromic), serum ferritin (low).
Treatment: Oral iron — Ferrous Sulphate 200mg (contains ~65mg elemental iron) TDS between 
meals for 3–6 months. Take with Vitamin C (orange juice). Avoid tea/coffee 1 hour before/after. 
Free IFA tablets under WIFS (adolescents), ANC, and ICDS programmes.
Dietary counselling: Green leafy vegetables (spinach, fenugreek, amaranth), jaggery, 
dried fruits, meat, fish, organ meats (liver), fortified foods.
Next steps: Clinical pallor assessment. Refer for Hb test. Initiate iron supplementation. 
Treat underlying causes (hookworm — Albendazole 400mg, malaria).
""",
        "tags": ["anaemia", "iron deficiency", "pallor", "fatigue", "koilonychia", "Hb", "nutrition"],
    },

    {
        "id": "vitamin_a_deficiency",
        "name": "Vitamin A Deficiency / Nutritional Blindness",
        "category": "Nutritional Deficiency",
        "icd10": "E50",
        "content": """
Disease: Vitamin A deficiency — leading preventable cause of blindness in children globally.
India has significant burden in underfive children.
Symptoms (graded): Night blindness (nyctalopia) — earliest symptom, child cannot see in dim 
light. Conjunctival xerosis (dry conjunctiva). Bitot's spots (foamy/cheesy white spots on 
conjunctiva — pathognomonic). Corneal xerosis → corneal ulceration (keratomalacia) → 
permanent blindness. Increased susceptibility to infections (measles, diarrhoea, ARI).
Diagnosis: Clinical eye examination. Serum retinol (< 0.7 µmol/L = deficient).
Treatment: Vitamin A capsules — Massive Dose Supplementation (MDS):
  - 6–11 months: 100,000 IU
  - 12–59 months: 200,000 IU (every 6 months)
  Free distribution under NHP/ICDS at 6-monthly intervals.
  Therapeutic dose (xerophthalmia): same doses on day 1, day 2, and day 14.
Next steps: Visual assessment — ask about night blindness (Hemeralopia). Examine conjunctiva 
for Bitot's spots. Refer to ophthalmologist for corneal involvement. Ensure routine VAS under ICDS.
Dietary: Orange/yellow vegetables, dark green leafy vegetables, eggs, liver, dairy.
""",
        "tags": ["vitamin A", "blindness", "night blindness", "Bitot's spots", "child", "nutrition", "eye"],
    },

    # ══════════════════════════════════════════════════════════
    # MENTAL HEALTH
    # ══════════════════════════════════════════════════════════

    {
        "id": "depression",
        "name": "Depression",
        "category": "Mental Health",
        "icd10": "F32",
        "content": """
Disease: Major Depressive Disorder — common mental health condition significantly under-diagnosed 
in rural India. Stigma is a major barrier to care-seeking.
Symptoms: Persistent sadness or low mood (most days, ≥ 2 weeks), loss of interest in 
previously enjoyed activities (anhedonia), reduced energy/fatigue, poor concentration, 
sleep disturbance (insomnia or hypersomnia), appetite change (weight loss or gain), 
feelings of worthlessness or guilt, hopelessness, reduced libido. 
Somatic presentations common in India: headache, bodily pains, 'pressure in head', 
digestive complaints without organic cause.
Suicidal ideation: Always ask sensitively about thoughts of self-harm or ending life — 
'Have you felt life is not worth living?'
Triage: EMERGENCY if active suicidal ideation with plan. URGENT for severe depression 
or postpartum depression. NORMAL for mild depression with psychosocial support.
Screening: PHQ-9 tool (locally validated). ASSIST for alcohol/substance comorbidity.
Treatment: Psychosocial support, structured activities, lifestyle changes. Antidepressants 
(SSRIs — Fluoxetine, Escitalopram) for moderate/severe under doctor prescription. 
MHPSS under NMHP (National Mental Health Programme) — counselling at PHC.
Next steps: Build rapport, non-judgemental assessment. Screen for suicide. 
Refer to medical officer/DMHP for antidepressant initiation. Mobilise social support. 
Follow up in 2 weeks.
""",
        "tags": ["depression", "sadness", "mental health", "fatigue", "sleep", "anhedonia", "mood"],
    },

    # ══════════════════════════════════════════════════════════
    # EMERGENCY CONDITIONS
    # ══════════════════════════════════════════════════════════

    {
        "id": "snake_bite",
        "name": "Snakebite",
        "category": "Emergency / Envenomation",
        "icd10": "T63.0",
        "content": """
Disease: Snakebite — medical emergency. India has 1.2 million snakebite deaths per decade 
(highest in world). Big 4 venomous snakes: Russell's Viper, Saw-scaled Viper (haemotoxic), 
Common Krait, Spectacled Cobra (neurotoxic).
Haemotoxic venom signs: Swelling, pain, bleeding from bite site, bleeding gums/wounds, 
haematuria (blood in urine), coagulopathy, tissue necrosis.
Neurotoxic venom signs: Little local swelling, drooping eyelids (ptosis), double vision, 
slurred speech, difficulty swallowing, muscle paralysis, respiratory failure (FATAL if untreated).
Triage: EMERGENCY — all venomous snakebites are emergencies. Time-critical.
DO:
  - Immobilise bitten limb (splint like a fracture) — reduces venom spread
  - Lie patient down — limit movement
  - Remove jewellery/tight items from bitten limb
  - Transport immediately to nearest hospital with ASV (Anti-Snake Venom)
  - Note time of bite and if snake was seen/killed
  - Pressure immobilisation for neurotoxic bites (NOT for haemotoxic/viper bites)
DO NOT:
  - Do NOT cut and suck wound
  - Do NOT apply tourniquet (causes tissue death)
  - Do NOT apply traditional remedies (temple, tying stone)
  - Do NOT give alcohol
  - Do NOT delay transport
Treatment: Polyvalent ASV (Anti-Snake Venom) — effective against Big 4. 
Given IV at hospital. 20-min whole blood clotting test to assess coagulopathy.
Next steps: Transport IMMEDIATELY. Do first aid as above. Call 108.
""",
        "tags": ["snakebite", "snake", "emergency", "venom", "bite", "neurotoxic", "haemotoxic"],
    },

    {
        "id": "heatstroke",
        "name": "Heat Stroke / Heat Exhaustion",
        "category": "Emergency / Environmental",
        "icd10": "T67.0",
        "content": """
Disease: Heat stroke — thermoregulatory failure with core body temperature > 40°C and 
CNS dysfunction. Medical emergency. Common in rural India during summer (March–June), 
especially in outdoor workers (farmers, labourers).
Classic heat stroke: Elderly in hot environment, dry skin (no sweating), confusion.
Exertional heat stroke: Young workers doing heavy labour in heat, may still be sweating.
Symptoms of heat stroke: Very high body temperature (>40°C), hot dry skin (or sweating 
in exertional), confusion/delirium/loss of consciousness, seizures, rapid pulse, 
rapid breathing, low BP (shock), nausea/vomiting.
Heat exhaustion (less severe): Heavy sweating, pale clammy skin, weakness, dizziness, 
nausea, fainting — temperature < 40°C, no confusion.
Triage: EMERGENCY for heat stroke. URGENT for heat exhaustion.
Immediate cooling (most critical intervention):
  1. Remove from hot environment — shade, cool room
  2. Remove excess clothing
  3. Aggressive cooling: Wet sheets/cloths + fanning, ice packs to neck/axilla/groin, 
     cold water immersion if available
  4. Fan aggressively
  5. Cool IV fluids if available (avoid Ringer's lactate if seizure risk)
  6. GOAL: Reduce temperature to 39°C as quickly as possible
  7. Call 108 — transport to hospital
  8. Monitor consciousness, breathing, pulse
Next steps: Start cooling immediately — do not wait for ambulance. Prevent by staying 
hydrated, avoiding peak sun (11am–3pm), wearing light clothing, rest in shade.
""",
        "tags": ["heat stroke", "high temperature", "confusion", "hot weather", "emergency", "summer"],
    },

    {
        "id": "rabies_animal_bite",
        "name": "Rabies / Animal Bite",
        "category": "Emergency / Zoonotic",
        "icd10": "T14.1 / A82",
        "content": """
Disease: Rabies — almost 100% fatal once symptoms appear. India accounts for 36% of 
world's rabies deaths (~20,000/year). Transmitted by bite/scratch of rabid animals 
(dogs — 97% in India, cats, monkeys, bats).
Wound categories (WHO):
  Category I: Touching/feeding animal, licks on intact skin → No PEP needed, just wash.
  Category II: Minor scratches/abrasions without bleeding, nibbling on uncovered skin → 
  Wound wash + Vaccine only.
  Category III: Single/multiple transdermal bites or scratches, licks on broken skin, 
  contamination of mucous membrane, bat exposure → Wound wash + Vaccine + RIG (Rabies 
  Immunoglobulin) immediately.
Critical first aid — wound washing: Immediately wash wound with running water and soap 
for 15 minutes. Apply Povidone-Iodine or alcohol. This ALONE reduces rabies risk by up to 80%.
Triage: URGENT for Category II. EMERGENCY for Category III (RIG needed within 7 days 
of first vaccine dose). All animal bites should be treated as potential rabies exposure.
Treatment: 
  - Anti-Rabies Vaccine (ARV): Intradermal (IDRV — cost-effective) or Intramuscular. 
    Updated Thai Red Cross regimen: Days 0, 3, 7, 28 (4-dose schedule).
  - Rabies Immunoglobulin (ERIG/HRIG): Infiltrated around wound for Category III. 
    Available at district hospitals.
  - Do NOT suture wound immediately (increases viral load). Do NOT apply tight bandage.
  - Tetanus prophylaxis.
Next steps: WASH WOUND IMMEDIATELY with soap and water (15 min). Apply antiseptic. 
Refer to nearest ARV centre (PHC/CHC/district hospital). Start vaccine on Day 0. 
Do NOT delay — rabies is 100% fatal once symptomatic.
Observe the biting dog for 10 days if possible (if healthy after 10 days, can stop vaccine).
""",
        "tags": ["rabies", "dog bite", "animal bite", "emergency", "vaccine", "wound", "cat bite"],
    },

    {
        "id": "scorpion_sting",
        "name": "Scorpion Sting",
        "category": "Emergency / Envenomation",
        "icd10": "T63.2",
        "content": """
Disease: Scorpion sting — common emergency in rural India, especially in Maharashtra, 
AP, Tamil Nadu, Rajasthan. Indian Red Scorpion (Mesobuthus tamulus) is the most dangerous 
scorpion in the world — cardiotoxic venom.
Symptoms: 
  Local: Severe burning pain at sting site, swelling, numbness.
  Systemic (within 30–60 min in severe cases): Profuse sweating, salivation, 
  vomiting, abdominal pain, tachycardia then bradycardia, hypertension then shock, 
  pulmonary oedema (frothy sputum, breathlessness — life-threatening), 
  priapism (sustained erection), agitation/encephalopathy.
Children: More likely to develop severe envenomation — lower body weight means higher 
venom-to-weight ratio. Can die within hours.
Triage: EMERGENCY if any systemic symptoms. URGENT if local symptoms only in adult. 
EMERGENCY for ALL scorpion stings in children <10 years.
Treatment:
  - First aid: Ice pack to sting site for pain. Paracetamol for pain.
  - Prazosin (alpha-blocker) is LIFE-SAVING for scorpion envenomation:
    Adults: 0.5mg oral, repeat every 3 hours until symptoms resolve.
    Children: 30 mcg/kg/dose oral.
  - For pulmonary oedema: IV Nitroprusside/Dobutamine at hospital + oxygen.
  - NO tourniquet. NO incision.
Next steps: Give Prazosin immediately if available (many PHCs stock it). 
Monitor BP, heart rate. Refer urgently if child or any systemic signs. 
Keep patient warm. Transport to nearest hospital.
""",
        "tags": ["scorpion", "sting", "emergency", "pain", "sweating", "Prazosin", "cardiotoxic"],
    },

    {
        "id": "burn_injury",
        "name": "Burn Injury",
        "category": "Emergency / Trauma",
        "icd10": "T20-T32",
        "content": """
Disease: Burns — thermal injury. Very common in rural India due to open cooking fires, 
kerosene stoves, biomass fuel. Women and children most affected. Burns >20% BSA in 
adults or >10% in children/elderly are life-threatening.
Classification:
  - First degree (superficial): Red, painful, dry. No blisters. Heals 3–5 days. (Sunburn)
  - Second degree (partial thickness): Blisters, very painful, moist pink base under blisters. 
    Heals 2–3 weeks. May scar.
  - Third degree (full thickness): White/charred/leathery, painless (nerve destruction), 
    dry. Requires skin grafting.
Rule of Nines (adult areas): Head 9%, each arm 9%, each leg 18%, front trunk 18%, 
back trunk 18%, perineum 1%. Palm of patient's hand ≈ 1% BSA.
Triage: EMERGENCY if >20% BSA, burns on face/neck/hands/genitals, inhalation injury 
(singed nasal hairs, soot in mouth, hoarseness), electrical/chemical burns, circumferential 
burns. URGENT for moderate burns. NORMAL for minor burns <10% superficial.
Immediate management:
  1. STOP BURNING PROCESS — remove from heat, remove burning clothing
  2. COOL with clean running water for 20 minutes (NOT ice)
  3. Cover with clean cloth/cling film (do NOT apply butter/toothpaste/egg/mud)
  4. Elevate burnt limb
  5. Pain relief: oral/IM Paracetamol or Ibuprofen
  6. IV fluids for >15% BSA burns — Parkland formula
  7. Tetanus prophylaxis
  8. Refer if criteria met
Next steps: Cool immediately. Cover. Do NOT break blisters. Do NOT apply traditional 
remedies. Pain relief. Urgent referral if criteria met. Counsel on fire safety.
""",
        "tags": ["burn", "fire", "blister", "scald", "emergency", "skin", "pain"],
    },

    {
        "id": "tetanus",
        "name": "Tetanus",
        "category": "Emergency / Infectious",
        "icd10": "A35",
        "content": """
Disease: Tetanus — caused by Clostridium tetani toxin (tetanospasmin). Enters through 
contaminated wounds (soil, rust, faeces). Still occurs in rural India, including neonatal 
tetanus from unclean cord cutting.
Symptoms: Trismus / lockjaw (inability to open mouth — usually first symptom), 
risus sardonicus (fixed grimace/smile), generalized muscle rigidity and spasms 
(opisthotonus — arching of back), difficulty swallowing, abdominal rigidity 
('board-like abdomen'), painful muscle spasms triggered by noise/touch/light. 
Spasms can cause fractures and respiratory failure.
Neonatal tetanus: Baby stops feeding, becomes rigid, has spasms — usually fatal without treatment.
Triage: EMERGENCY — all tetanus is a medical emergency. ICU admission required.
Tetanus-prone wounds: Deep/puncture wounds, crush injuries, bites, soil-contaminated wounds, 
wounds with dead tissue, burns, frostbite. Duration >6 hours since injury.
Treatment: 
  - Human Tetanus Immunoglobulin (HTIG) 500 IU IM immediately
  - Wound debridement (remove dead tissue, foreign material)
  - Antibiotics: Metronidazole IV (preferred over Penicillin)
  - Muscle relaxants: IV Diazepam, Magnesium Sulphate
  - ICU for airway management, mechanical ventilation if needed
  - Active immunisation: TT/Td vaccine (immunity is NOT conferred by disease)
Next steps: Immediate hospital referral. Give TT vaccine if not up to date. 
Do NOT close wound. Wound cleaning. Dark quiet room (reduces spasm triggers).
Prevention: TT vaccination (5-dose schedule in NIS), clean cord cutting practices, 
proper wound care and tetanus prophylaxis for all wounds.
""",
        "tags": ["tetanus", "lockjaw", "spasm", "wound", "emergency", "trismus", "rigidity"],
    },

    # ══════════════════════════════════════════════════════════
    # EYE / ENT
    # ══════════════════════════════════════════════════════════

    {
        "id": "acute_conjunctivitis",
        "name": "Acute Conjunctivitis (Pink Eye / Aankh Aana)",
        "category": "Eye",
        "icd10": "H10",
        "content": """
Disease: Conjunctivitis — inflammation of the conjunctiva. Very common in rural India, 
mass outbreaks in schools and crowded settings. Called 'Aankh Aana' in Hindi.
Types:
  Viral (commonest epidemic form): Watery discharge, bilateral, itching, associated URTI, 
  pre-auricular lymph node. Highly contagious. Self-limiting 7–14 days.
  Bacterial: Mucopurulent thick yellow-green discharge, eyelids stuck on waking, 
  unilateral or bilateral. Staphylococcus, Streptococcus, H. influenzae.
  Allergic: Intense itching, watery discharge, bilateral, seasonal, associated with 
  allergic rhinitis. Papillae on conjunctiva.
Danger signs (refer urgently): Eye pain (not just irritation), reduced vision, corneal 
opacity (white spot on cornea), photophobia, history of chemical splash — these suggest 
keratitis or other serious condition, NOT simple conjunctivitis.
Triage: NORMAL for simple conjunctivitis. URGENT if pain, reduced vision, corneal involvement. 
EMERGENCY if chemical injury (immediate irrigation for 30 min then refer).
Treatment:
  - Viral: Cool compresses, artificial tears. Resolves on its own 7–14 days.
  - Bacterial: Topical antibiotic eye drops — Ciprofloxacin 0.3% or Chloramphenicol 1% 
    eye drops, 1 drop 4 times daily for 5–7 days. Clean eyes with cotton wool + boiled water.
  - Allergic: Antihistamine eye drops (Olopatadine), cold compress, avoid allergen.
Next steps: Hand washing education (prevent spread). Avoid sharing towels. No school for 
viral (until discharge clears). Use clean cotton for each eye. Refer if any danger sign.
""",
        "tags": ["conjunctivitis", "pink eye", "eye", "red eye", "discharge", "itching", "aankh aana"],
    },

    {
        "id": "acute_otitis_media",
        "name": "Acute Otitis Media (Ear Infection)",
        "category": "ENT",
        "icd10": "H66",
        "content": """
Disease: Acute Otitis Media (AOM) — middle ear infection. Extremely common in children 
(peak 6 months–3 years). Can lead to hearing loss if untreated/recurrent — significant 
cause of preventable deafness in rural India.
Symptoms: Ear pain (otalgia) — child pulls/tugs ear, irritable, crying especially at night. 
Fever. Hearing reduction. Ear discharge (otorrhoea — if tympanic membrane has perforated, 
paradoxically pain improves). Sleep disturbance. In young children: irritability, poor feeding, 
pulling at ear, fever — non-specific.
Chronic Suppurative Otitis Media (CSOM): Persistent ear discharge >2 weeks through perforated 
tympanic membrane — common in rural India, can cause permanent hearing loss.
Triage: URGENT if severe pain, high fever, swelling behind ear (mastoiditis — EMERGENCY), 
facial weakness. NORMAL for uncomplicated AOM.
Danger signs — refer immediately: Swelling/redness behind ear (mastoiditis), facial weakness/
drooping, severe headache with stiff neck (meningitis), vertigo, recent worsening despite treatment.
Treatment: 
  - Mild AOM: Observation for 48–72 hours + Paracetamol for pain relief.
  - Moderate/Severe/Age <2: Amoxicillin oral (80–90 mg/kg/day) for 7–10 days (first line).
  - CSOM: Aural toilet (dry mopping with cotton wick) + topical Ciprofloxacin ear drops. 
    Refer to ENT specialist if not resolving.
  - Warm compress over ear for pain.
Next steps: Pain management first. Watch for danger signs. Complete antibiotic course. 
Refer to ENT if recurrent (3+ episodes in 6 months) or persistent discharge.
Prevention: Breastfeeding, avoid bottle-feeding lying flat, pneumococcal vaccine, handwashing.
""",
        "tags": ["ear pain", "ear infection", "otitis", "discharge", "hearing", "child", "fever", "ENT"],
    },

    # ══════════════════════════════════════════════════════════
    # GENITOURINARY
    # ══════════════════════════════════════════════════════════

    {
        "id": "urinary_tract_infection",
        "name": "Urinary Tract Infection (UTI)",
        "category": "Genitourinary",
        "icd10": "N39.0",
        "content": """
Disease: UTI — bacterial infection of urinary tract. Very common in women (short urethra, 
proximity to perineum). Under-reported in rural India due to stigma around genital symptoms.
Types: Lower (cystitis — bladder), Upper (pyelonephritis — kidney — more serious).
Symptoms (lower UTI/cystitis): Burning during urination (dysuria), frequent urination, 
urgency, suprapubic pain/discomfort, cloudy or foul-smelling urine, occasional haematuria 
(blood in urine). Usually NO fever.
Symptoms (upper UTI/pyelonephritis): All of above PLUS high fever with chills, flank/back 
pain (costovertebral angle tenderness), nausea/vomiting, malaise — systemic illness.
Triage: NORMAL for uncomplicated lower UTI in non-pregnant woman. URGENT for pyelonephritis, 
UTI in pregnancy, UTI in males/children (suggests structural abnormality), recurrent UTI. 
EMERGENCY if sepsis signs (high fever, low BP, confusion).
Diagnosis: Urine dipstick (leukocytes + nitrites), urine culture.
Treatment:
  - Uncomplicated cystitis: Nitrofurantoin 100mg BD for 5 days, OR Fosfomycin single 3g dose.
  - Pyelonephritis: Oral Ciprofloxacin or Ceftriaxone IM. Severe: IV antibiotics + hospitalisation.
  - Pregnancy: Safe options — Nitrofurantoin (not in 3rd trimester), Amoxicillin, Cephalexin.
  - Adequate fluid intake (2–3 litres/day).
Next steps: Encourage fluid intake. Refer for urine test. Complete antibiotic course. 
Counsel: wipe front to back, urinate after intercourse, avoid holding urine, 
cotton underwear. Refer if fever, flank pain, pregnancy, or recurrence.
""",
        "tags": ["UTI", "burning urine", "dysuria", "urinary", "frequency", "kidney", "bladder"],
    },

    # ══════════════════════════════════════════════════════════
    # GENETIC / HAEMATOLOGICAL
    # ══════════════════════════════════════════════════════════

    {
        "id": "sickle_cell_disease",
        "name": "Sickle Cell Disease",
        "category": "Genetic / Haematological",
        "icd10": "D57",
        "content": """
Disease: Sickle Cell Disease (SCD) — inherited haemoglobinopathy (HbSS). Sickle-shaped 
RBCs cause vaso-occlusion. Highly prevalent in tribal populations of Central India 
(Chhattisgarh, MP, Maharashtra — tribal belt prevalence 10–35% carriers, 1–2% disease).
Symptoms: 
  Vaso-occlusive crisis (VOC — most common): Severe bone pain (arms, legs, back, chest), 
  often triggered by cold, dehydration, infection. Pain can be excruciating. 
  Hand-foot syndrome (dactylitis) in young children — first presentation.
  Chronic anaemia: Pallor, fatigue, jaundice, dark urine (haemolysis).
  Splenic sequestration crisis (children): Sudden spleen enlargement, severe anaemia, shock — EMERGENCY.
  Acute chest syndrome: Fever, chest pain, cough, hypoxia — EMERGENCY (leading cause of death in SCD).
  Stroke: Can occur in children with SCD — face drooping, arm weakness.
  Priapism: Painful sustained erection — urological emergency.
Triage: EMERGENCY for chest syndrome, splenic sequestration, stroke, priapism, or severe crisis. 
URGENT for moderate VOC. NORMAL for routine monitoring.
Treatment:
  - VOC: Aggressive IV hydration, strong pain relief (Paracetamol + NSAIDs + Tramadol/Morphine), 
    oxygen if SpO2 < 95%. Folic acid 5mg daily (lifelong). Avoid cold, dehydration.
  - Hydroxyurea (disease-modifying): Reduces crisis frequency by 50%. Available free under RBSK. 
    1000mg/day adults. Monitor blood counts.
  - Blood transfusion for severe anaemia (Hb < 5 g/dL), acute chest, sequestration.
  - Preventive: Penicillin V prophylaxis in children <5 years (prevents pneumococcal sepsis).
  - Pneumococcal, meningococcal, Hep B, influenza vaccinations.
Next steps: Screen tribal populations (RBSK covers this). Solubility test + HPLC confirmation. 
Register in Sickle Cell Mission (Government programme). Genetic counselling for carriers.
Ensure Hydroxyurea compliance. Educate on triggers (cold, dehydration, high altitude).
""",
        "tags": ["sickle cell", "bone pain", "anaemia", "jaundice", "tribal", "crisis", "haemoglobin"],
    },

    # ══════════════════════════════════════════════════════════
    # NEUROLOGICAL
    # ══════════════════════════════════════════════════════════

    {
        "id": "epilepsy_seizure",
        "name": "Epilepsy / Seizure Disorder",
        "category": "Neurological",
        "icd10": "G40",
        "content": """
Disease: Epilepsy — chronic neurological condition with recurrent unprovoked seizures. 
Prevalence ~6 per 1000 in India. Massively stigmatised in rural areas — many patients 
hide condition or seek traditional/faith healers instead of medical treatment.
Seizure types:
  Generalised tonic-clonic (grand mal): Sudden loss of consciousness, body stiffens (tonic), 
  followed by rhythmic jerking (clonic), drooling/frothing, may bite tongue, urinary 
  incontinence. Postictal: confused, sleepy, headache (minutes–hours).
  Absence (petit mal): Brief staring spells (5–30 sec), more common in children, 
  often missed — mistaken for daydreaming.
  Focal: Twitching of face/arm/leg, unusual sensations, aura (déjà vu, smell), 
  can progress to generalised.
Status epilepticus: Continuous seizure >5 min or repeated seizures without regaining 
consciousness — EMERGENCY, can be fatal.
First aid during a seizure (ASHA training):
  DO: Note time. Place in recovery position. Protect from injury (cushion head). 
  Loosen tight clothing. Stay until fully conscious.
  DO NOT: Put anything in mouth. Restrain. Give water/food during/immediately after seizure.
  Call 108 if: seizure lasts >5 min, no previous seizure history, multiple seizures, 
  injury during seizure, not regaining consciousness.
Triage: EMERGENCY for status epilepticus or first-ever seizure. URGENT for uncontrolled epilepsy 
or change in seizure pattern. NORMAL for well-controlled epilepsy on medication.
Treatment: Anti-epileptic drugs (AEDs) — Carbamazepine, Valproic acid, Phenytoin, Levetiracetam. 
Free under NMHP at PHC. Monotherapy preferred. Must NOT be stopped suddenly — risk of 
status epilepticus. Regular lifelong medication in most cases.
For status epilepticus: IV Diazepam (0.2 mg/kg) or rectal Diazepam, then IV Phenytoin loading.
Next steps: Refer for EEG and neurologist evaluation. Educate family on first aid. 
Counsel against stigma — epilepsy is a treatable medical condition, NOT possession/curse. 
Ensure medication compliance (daily AED). Driving/swimming restrictions.
""",
        "tags": ["epilepsy", "seizure", "convulsion", "fits", "unconscious", "jerking", "neurological"],
    },

    # ══════════════════════════════════════════════════════════
    # DROWNING
    # ══════════════════════════════════════════════════════════

    {
        "id": "drowning_near_drowning",
        "name": "Drowning / Near-Drowning",
        "category": "Emergency / Trauma",
        "icd10": "T75.1",
        "content": """
Disease: Drowning — a leading cause of death in children (1–14 years) in rural India. 
Open wells, ponds, irrigation canals, rivers are common sites. Often preventable.
Recognition: Found in/near water, unconscious, not breathing, cyanosis (blue lips/skin), 
water from mouth/nose, hypothermia, vomiting.
Triage: EMERGENCY — every second counts. Brain damage begins within 4–6 minutes without oxygen.
Immediate rescue actions:
  1. Remove from water SAFELY (do not become a victim — use rope/stick/float)
  2. Place on flat surface
  3. Check responsiveness — tap shoulders, shout
  4. Open airway — head tilt, chin lift (jaw thrust if spinal injury suspected)
  5. Check breathing (look, listen, feel for 10 seconds)
  6. If NOT breathing: Start CPR immediately
     - 5 rescue breaths first (drowning is respiratory arrest)
     - Then 30 chest compressions: 2 breaths ratio
     - Compression depth: 5 cm adults, 1/3 chest depth children
     - Rate: 100–120/minute
     - Continue until breathing resumes or ambulance arrives
  7. If breathing: Place in recovery position (left lateral)
  8. Call 108 ambulance
Do NOT: Attempt to drain water from lungs (Heimlich manoeuvre NOT indicated in drowning). 
Do NOT delay CPR. Do NOT give up — cold water submersion survivors have recovered even 
after prolonged submersion.
Next steps: Start CPR immediately. Call 108. Transport to hospital even if recovered 
(secondary drowning/pulmonary oedema can occur hours later). Monitor closely for 24 hours.
Prevention: Supervise children near water. Fence open wells. Teach swimming. 
Cover irrigation channels. Community awareness programmes.
""",
        "tags": ["drowning", "near drowning", "CPR", "emergency", "child", "water", "unconscious", "rescue"],
    },
]


def get_all_documents() -> list:
    """Return list of (id, text, metadata) tuples for indexing."""
    docs = []
    for d in DISEASE_KNOWLEDGE_BASE:
        text = f"Disease: {d['name']}\nCategory: {d['category']}\n{d['content'].strip()}"
        metadata = {
            "name": d["name"],
            "category": d["category"],
            "icd10": d.get("icd10", ""),
            "tags": ", ".join(d.get("tags", [])),
        }
        docs.append((d["id"], text, metadata))
    return docs
