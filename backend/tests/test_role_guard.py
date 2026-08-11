import pytest
from app.rag.role_guard import find_missing_required_role, load_roles

REQUIREMENTS = {
    "muayene_onaylama": {
        "required_roles": ["Muayene Onay Personeli"],
        "trigger_terms": ["kendi muayenesini kendisi onaylayabilir"],
    }
}

def make_chunk(content: str, score: float | None = None) -> dict:
    chunk = {"content": content}
    if score is not None:
        chunk["score"] = score
    return chunk

def test_no_role_info_is_not_blocked():
    roles = load_roles()
    chunks = [make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.")]
    assert find_missing_required_role(chunks, [], roles, REQUIREMENTS) is None

def test_admin_always_passes():
    roles = load_roles()
    chunks = [make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.")]
    assert find_missing_required_role(chunks, ["Admin"], roles, REQUIREMENTS) is None

def test_matching_role_passes():
    roles = load_roles()
    chunks = [make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.")]
    assert find_missing_required_role(chunks, ["Muayene Onay Personeli"], roles, REQUIREMENTS) is None

def test_mismatched_role_is_blocked():
    roles = load_roles()
    chunks = [make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.")]
    result = find_missing_required_role(chunks, ["Muayene Personeli"], roles, REQUIREMENTS)
    assert result == "Muayene Onay Personeli"

def test_multi_role_user_with_one_match_passes():
    roles = load_roles()
    chunks = [make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.")]
    user_roles = ["Muayene Personeli", "Muayene Onay Personeli"]
    assert find_missing_required_role(chunks, user_roles, roles, REQUIREMENTS) is None

def test_chunk_without_trigger_terms_passes_for_anyone():
    roles = load_roles()
    chunks = [make_chunk("Genel bir kullanım sorusu, onay konusuyla ilgisi yok.")]
    assert find_missing_required_role(chunks, ["Muayene Personeli"], roles, REQUIREMENTS) is None

def test_only_checks_the_lowest_score_chunk_ignores_the_rest():
    roles = load_roles()
    chunks = [
        make_chunk("Genel bilgi, tetikleyici terim yok.", score=0.30),
        make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.", score=0.80),
    ]
    result = find_missing_required_role(chunks, ["Muayene Personeli"], roles, REQUIREMENTS)
    assert result is None

def test_checks_the_lowest_score_chunk_even_if_it_is_not_first_in_the_list():
    roles = load_roles()
    chunks = [
        make_chunk("Genel bilgi, tetikleyici terim yok.", score=0.80),
        make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir.", score=0.30),
    ]
    result = find_missing_required_role(chunks, ["Muayene Personeli"], roles, REQUIREMENTS)
    assert result == "Muayene Onay Personeli"

REAL_CONTENT_CASES = [
    (
        "muayene_onaylama",
        "Muayeneyi Onaya Gönderme Akışı\n"
        "Muayenenin onaya gönderilebilmesi için sistem kontrollerinden geçmiş olması gerekir. "
        "Onaylayan seçimi. Onaya gönderirken açıklama yazılabilir. Muayeneyi yapan kişi onay "
        "yetkisine de sahipse kendi muayenesini kendisi onaylayabilir; muayene kaydı "
        "güncellenerek onaylayan kişi veya muayene tarih/saati değiştirilebilir.",
        "Muayene Onay Personeli",
    ),
    (
        "cihaz_ekle",
        "Yeni Cihaz Ekle ekranında; Cihaz Adı, Cihaz Kodu, Seri No, İmalatçı/Markal, Model, "
        "Kalibrasyon Sapma Değeri, Cihaz Hassasiyeti, Periyodik Kontrol bilgileri, Ölçüm Cihazı mı?, "
        "Ölçüm cihazı ise hangi ölçüm cihazı olduğu seçimi girildikten ve varsa Cihaz Evrakları "
        "yüklendikten sonra durumu aktif seçerek cihaz oluşturulur.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "cihaz_zimmet_listesi",
        "Cihaz Yönetimi - Zimmet Listesi\n"
        "Cihazların zimmet kayıt bilgilerinin alınabilmesi ve zimmet dosyalarının yüklenebilmesi için "
        "geliştirme yapılmıştır. MUAYENE/ISO 17020 > Tanımlamaları > Cihaz Tanımlamları > Cihaz Detayı "
        "menüsündeki 'Zimmetlenen Personeller' alanından zimmet kayıtları ekleme - güncelleme - silme "
        "işlemleri yapılabilmektedir.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "yeni_firma_olusturma",
        "Yeni Firma Oluştur menüsünden yeni firma oluşturabilirsiniz. İlk olarak firma temel bilgilerini "
        "giriniz. Bu arada firma adı girmeniz zorunludur ve daha önceden bu ada sahip bir firma "
        "olmamalıdır. Firma ticari ünvanı muayene raporlarında gelecek isim olduğundan bu alanında "
        "girilmesi gerekmektedir.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "kisiler_yonetimi",
        "Kişiler Yönetimi\n"
        "MUAYENE/ISO 17020 > Tanımlamaları > Kişiler Yönetimi menüsünde sistemde var olan "
        "firmalarınızda bulunan kişileri listeleyebilir, görüntüleyebilir, düzenleyebilir veya gerekirse "
        "silebilirsiniz. Firmaya yeni kişi eklemek için Kişi Ekle menüsüne firmaya eklenecek kişi ile "
        "ilgili gerekli bilgileri girdikten sonra Oluştur butonuna basılır.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "muayene_kapsamlari_tanimlama",
        "1-Kapsamlar\n"
        "Muayeneye hizmetlerinin ana kapsamları girmektedir. Örneğin Elektirik, Mekanik, Yangın Algılama "
        "gibi… Muayene Kapsamları menüsü açıldıktan sonra Yeni Ekle butonuna basılır. Kapsam sorumlusu, "
        "kapsama bağlı hizmete onay personeli atanmaması durumunda ilgili hizmetin raporunun birinci "
        "onay veren kişisi olarak seçili gelecektir.",
        "Muayene Hizmetleri Konfigürasyonu",
    ),
    (
        "muayene_metodlari_tanimlama",
        "2-Muayene Metodları\n"
        "Muayene raporlarında metod seçimi yapılacak ise metodlar bu menüden girilmelidir. Yeni eklemek "
        "için Muayene Metotları menüsüne girdikten sonra sağ kısımda bulunan Yeni Ekle butonuna basılır. "
        "Metod adı ve Metod numarası yazılıp, metod türü seçimi yapılarak Oluştur butonuna basılarak "
        "metodlar oluşturulur.",
        "Muayene Hizmetleri Konfigürasyonu",
    ),
    (
        "muayene_hizmetleri_tanimlama",
        "3-Muayene Hizmetleri\n"
        "Muayene hizmetlerimizi tanımladığımız menüdür. İş emri oluştururken bu menüde tanımlı hizmetler "
        "gelmektedir. Açılan sayfada Muayene hizmetinin ismi, hangi kapsama bağlı olduğu, kontrol "
        "periyodu, isg katip katogorisi ve akredite durumu seçilip hizmet oluşturulur.",
        "Muayene Hizmetleri Konfigürasyonu",
    ),
    (
        "is_emri_dokumanlari_tanimlama",
        "4- İş Emri Dökümanları\n"
        "İş emirleri detayından rapor formları dışında alabileceğiniz dokümanları ekleyebileceğiniz "
        "menüdür. Yeni Ekle kısmından (saha görevlendirme, görev bildirim formu vbz) dokümanlarınızı "
        "ekleyebilirsiniz.",
        "Muayene Hizmetleri Konfigürasyonu",
    ),
    (
        "is_emri_yonetimi_gorme",
        "İş Emri Sorumlusu ile İş Emri Yöneticisi Farkı\n"
        "İş emri yöneticisi yetkisine sahip kullanıcı sistemdeki tüm iş emirlerini görür ve tamamı üzerinde\n"
        "işlem yapar. İş emri sorumlusu yetkisine sahip kullanıcı ise iş emri oluşturabilir; ancak yalnızca\n"
        "kendi oluşturduğu veya kendisinin sorumlu olarak atandığı iş emirleri üzerinde işlem yapabilir.",
        "İş Emri Yöneticisi",
    ),
    (
        "is_emri_listesi_sorumlu_gorunumu",
        "İş Emri Listesi (Sorumlu Görünümü)\n"
        "MUAYENE/ISO 17020 > İş Emirleri > İş Emirleri Listesi altında iş emri sorumlusu yalnızca\n"
        "kendisinin sorumlu olarak atandığı iş emirlerini görür. Örneğin sorumlu olarak atanmış 7 iş emri.",
        "İş Emri Sorumlusu",
    ),
    (
        "faturalandirma_erisim_yetkisi",
        "Erişim Yetkisi\n"
        "Ödeme (faturalandırma kayıtları) ekranına admin yetkisine sahip kullanıcılar erişebilir. Admin\n"
        "dışında, \"17020 Ödeme İşlemleri\" yetkisi tanımlanmış kullanıcılar da bu ekrana erişebilir.",
        "Muayene|ISO 17020 Ödeme İşlemleri",
    ),
     (
        "cihaz_tamamlanan_kalibrasyonlar",
        "Tamamlanan Periyodik Kontroller ve Sonuç Geri Alma\n"
        "Girilen kontrol sonuçları iki yerden görüntülenir: MUAYENE/ISO 17020 > Tanımlamalar >\n"
        "Kalibrasyonlar > Tamamlanan Periyodik Kontroller menüsünde ve Cihaz Detayı ekranındaki\n"
        "Periyodik Kontrol Geçmişi",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "cihaz_yapilacak_kalibrasyonlar",
        "Cihazın kontrol tarihinin takip edilebilmesi için\n"
        "MUAYENE/ISO 17020 > Tanımlamalar > Kalibrasyonlar > Yapılacak Periyodik Kontroller menüsü\n"
        "kullanılır. Bu menüde \"Süresi geçenler\", \"1 Ay Kalanlar\", \"3 Ay Kalanlar\", \"6 Ay Kalanlar\" ve \"1\n"
        "Yıl Kalanlar\" filtreleriyle kolayca arama yapılabilir.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "sabit_karekod_etiketleme",
        "Değişken kare kodun aksine, sabit kare kod, tanımlamalar altındaki MUAYENE/ISO 17020 > Tanımlar > Sabit Karekod\n"
        "Etiketleme bölümünden yönetilir. Bu türde tek bir sabit QR kod, tüm ekipmanlara (örneğin 50\n"
        "ekipmanın tamamına) aynı şekilde yapıştırılır.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "company_admin",
        "KURULUŞ TEST - Müşteriler\n"
        "Bu ekrandaki listede sisteme tanımlanmış müşteri firmalar listelenir.\n"
        "Toplu kayıt oluşturma veya verileri toplu dışa aktarma işlemleri için Admin yetkili bir kullanıcı\n"
        "ile giriş yapmanız gerekir. Admin yetkili bir kullanıcı ile giriş yaptığınızda, bu ekranda ilgili\n"
        "işlem butonları görüntülenir. Hesaptaki \"Sistem Yöneticisi\" işareti bu butonları görünür\n"
        "kılmaz; işlem yalnızca Admin kullanıcı tipine açıktır.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "equipmentinventory_index",
        "KURULUŞ TEST - Ekipman Envanteri\n"
        "Müşterilere ait, muayene edilen ekipmanların envanter olarak tutulduğu ekran. Hangi firmada\n"
        "hangi ekipmanların bulunduğu buradan izlenir ve etiketleme işlemlerinin dayanağını\n"
        "oluşturur. Her kayıt, sahada karekod okutularak bir muayeneyle eşleştirilmiş somut bir\n"
        "ekipmanı temsil eder.",
        "Muayene|ISO 17020 Tanımlama",
    ),
    (
        "inspectionreportstats_companylist",
        "KURULUŞ TEST - Firmaları Excele Aktar\n"
        "Sistemde kayıtlı tüm firmaların temel bilgilerini Excel formatında dışa aktarmanızı sağlar.",
        "Muayene|ISO 17020 Veri Analizi",
    ),
    (
        "inspectionreportstats_workorderlist",
        "KURULUŞ TEST - Tüm İş Emirlerini Excele Aktar\n"
        "Sistemdeki tüm iş emirlerini detaylarıyla birlikte Excel formatında dışa aktarmanızı sağlar.",
        "Muayene|ISO 17020 Veri Analizi",
    ),
    (
        "inspectionreportstats_reportusedlist",
        "KURULUŞ TEST - İş Emri Uygulama Raporu\n"
        "Seçilen tarih aralığı ve firma filtresine göre oluşturulan bu rapor, her iş emri ve muayene\n"
        "hizmeti için tekliflendirme, planlama, uygulama, onay, imzalama ve gönderim durumlarını\n"
        "sayısal olarak özetler. Excel formatında dışa aktarılabilir.",
        "Muayene|ISO 17020 Veri Analizi",
    ),
    (
        "isgcontract_index",
        "KURULUŞ TEST - ISG Katip Sözleşmeleri\n"
        "Muayene personellerine ait İSG Katip sözleşmelerinin listelendiği, güncellendiği ve silindiği\n"
        "ekran. Bu modülde İSG-KATİP sözleşme bilgileri ve ilgili PDF dokümanı yönetilir; sözleşme\n"
        "numarasının rapora yansıtılması ve müşteriye gönderilen raporlar sonrasında yüklenen PDF\n"
        "dokümanın müşteri portalında gösterilmesi işlemleri sağlanır.",
        "ISG Katip Yöneticisi",
    ),
    (
        "workorder_listcreate",
        "KURULUŞ TEST - İş Emri Oluştur (Sorumlu)\n"
        "İş Emri Sorumlusu'nun kendisinin sorumlu olacağı yeni bir iş emri oluşturabildiği ekran. İş\n"
        "Emri Yönetimi altındaki \"İş Emri Oluştur\" ekranından (workorder/create) farklı bir rotadır.\n"
        "Ekran, İş Emri Sorumlusu yetkisine bağlıdır; İş Emri Yöneticisi yetkisi de bulunan kullanıcılar\n"
        "bu ekranı görmeye devam eder, ayrıca İş Emri Yönetimi altındaki İş Emri Oluştur ekranını da\n"
        "kullanabilir. Oluşturma adımları iki ekranda da aynıdır.",
        "İş Emri Sorumlusu",
    ),
]

@pytest.mark.parametrize("requirement_key,chunk_text,required_role", REAL_CONTENT_CASES)
def test_real_role_requirement_blocks_unauthorized_user(requirement_key, chunk_text, required_role):
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    assert requirement_key in role_requirements

    result = find_missing_required_role([make_chunk(chunk_text)], ["Muayene Personeli"], roles, role_requirements)
    assert result == required_role

@pytest.mark.parametrize("requirement_key,chunk_text,required_role", REAL_CONTENT_CASES)
def test_real_role_requirement_passes_for_authorized_user(requirement_key, chunk_text, required_role):
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()

    result = find_missing_required_role([make_chunk(chunk_text)], [required_role], roles, role_requirements)
    assert result is None

IS_EMIRLERI_TAKVIMI_CHUNK_TEXT = (
    "İş emirleri takviminden Taşıt Takvimi bölümü admin yetkisiyle görülür. Yalnızca iş emri sorumlusu\n"
    "yetkisi olan bir kullanıcıda üstteki admin menüsü hiç görünmez; muayene personeli\n"
    "yetkisiyle iş emri takvimi açıldığında ise kullanıcı yalnızca kendi görevli olduğu günleri görür,\n"
    "tüm personelin takvimini görmez."
)

@pytest.mark.parametrize("authorized_role", ["Muayene Onay Personeli", "Muayene Personeli"])
def test_is_emirleri_takvimi_passes_for_each_authorized_role(authorized_role):
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    assert "is_emirleri_takvimi_gorunumu" in role_requirements

    result = find_missing_required_role([make_chunk(IS_EMIRLERI_TAKVIMI_CHUNK_TEXT)], [authorized_role], roles, role_requirements)
    assert result is None


def test_is_emirleri_takvimi_blocks_unrelated_role():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()

    result = find_missing_required_role([make_chunk(IS_EMIRLERI_TAKVIMI_CHUNK_TEXT)], ["Muayene Hizmetleri Konfigürasyonu"], roles, role_requirements)
    assert result == "Muayene Onay Personeli"

def test_isgcontract_index_also_passes_for_muayene_yoneticisi():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    chunk_text = (
        "KURULUŞ TEST - ISG Katip Sözleşmeleri\n"
        "Muayene personellerine ait İSG Katip sözleşmelerinin listelendiği, güncellendiği ve silindiği\n"
        "ekran."
    )

    result = find_missing_required_role([make_chunk(chunk_text)], ["Muayene Yöneticisi"], roles, role_requirements)
    assert result is None

REQUIRED_ROLES_ALL_REQUIREMENTS = {
    "toplu_is_emri": {
        "required_roles_all": ["İş Emri Yöneticisi", "İş Emri Sorumlusu"],
        "trigger_terms": ["toplu şekilde oluşturulup yönetildiği ekran"],
    }
}


def test_required_roles_all_passes_when_user_has_every_role():
    roles = load_roles()
    chunks = [make_chunk("İş emirlerinin tek tek değil, toplu şekilde oluşturulup yönetildiği ekran.")]
    user_roles = ["İş Emri Yöneticisi", "İş Emri Sorumlusu"]
    assert find_missing_required_role(chunks, user_roles, roles, REQUIRED_ROLES_ALL_REQUIREMENTS) is None


def test_required_roles_all_not_applied_when_no_role_info():
    roles = load_roles()
    chunks = [make_chunk("İş emirlerinin tek tek değil, toplu şekilde oluşturulup yönetildiği ekran.")]
    assert find_missing_required_role(chunks, [], roles, REQUIRED_ROLES_ALL_REQUIREMENTS) is None


@pytest.mark.parametrize(
    "user_roles,expected_missing",
    [
        (["İş Emri Yöneticisi"], "İş Emri Sorumlusu"),
        (["İş Emri Sorumlusu"], "İş Emri Yöneticisi"),
        (["Muayene Personeli"], "İş Emri Yöneticisi"),
    ],
)
def test_required_roles_all_blocks_when_any_role_is_missing(user_roles, expected_missing):
    roles = load_roles()
    chunks = [make_chunk("İş emirlerinin tek tek değil, toplu şekilde oluşturulup yönetildiği ekran.")]
    result = find_missing_required_role(chunks, user_roles, roles, REQUIRED_ROLES_ALL_REQUIREMENTS)
    assert result == expected_missing

WORKORDER_LISTCREATE_REAL_TEXT = (
    "KURULUŞ TEST - İş Emri Oluştur (Sorumlu)\n"
    "İş Emri Sorumlusu'nun kendisinin sorumlu olacağı yeni bir iş emri oluşturabildiği ekran."
)
IS_EMRI_YONETICISI_FARKI_REAL_TEXT = (
    "İş Emri Sorumlusu ile İş Emri Yöneticisi Farkı\n"
    "İş emri yöneticisi yetkisine sahip kullanıcı sistemdeki tüm iş emirlerini görür ve tamamı üzerinde işlem yapar."
)

def test_workorder_listcreate_not_blocked_by_coretrieved_yoneticisi_farki_chunk():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    chunks = [
        make_chunk(WORKORDER_LISTCREATE_REAL_TEXT, score=0.4244),
        make_chunk(IS_EMRI_YONETICISI_FARKI_REAL_TEXT, score=0.4699),
    ]

    result = find_missing_required_role(chunks, ["İş Emri Sorumlusu"], roles, role_requirements)
    assert result is None

WORKORDER_BULKCREATE_CHUNK_TEXT = (
    "KURULUŞ TEST - Toplu İş Emri Oluştur\n"
    "İş emirlerinin tek tek değil, toplu şekilde oluşturulup yönetildiği ekran. Çok sayıda firma veya\n"
    "ekipman için aynı anda iş emri açılmasını sağlayarak planlama yükünü azaltır. Toplu İş\n"
    "Emirleri Oluştur ekranına erişebilmek için kullanıcıda hem İş Emri Yöneticisi hem İş Emri\n"
    "Sorumlusu yetkisinin aynı anda bulunması gerekir."
)


def test_workorder_bulkcreate_passes_for_user_with_both_roles():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    assert "workorder_bulkcreate" in role_requirements
    assert role_requirements["workorder_bulkcreate"]["required_roles_all"] == ["İş Emri Yöneticisi", "İş Emri Sorumlusu"]

    user_roles = ["İş Emri Yöneticisi", "İş Emri Sorumlusu"]
    result = find_missing_required_role([make_chunk(WORKORDER_BULKCREATE_CHUNK_TEXT)], user_roles, roles, role_requirements)
    assert result is None


def test_workorder_bulkcreate_blocks_user_with_only_one_role():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()

    result = find_missing_required_role([make_chunk(WORKORDER_BULKCREATE_CHUNK_TEXT)], ["İş Emri Yöneticisi"], roles, role_requirements)
    assert result == "İş Emri Sorumlusu"

COMPANY_ADMIN_REAL_TEXT = (
    "KURULUŞ TEST - Müşteriler\n"
    "Bu ekrandaki listede sisteme tanımlanmış müşteri firmalar listelenir."
)
MUAYENE_ONAYLAMA_REAL_TEXT = (
    "Muayeneyi Onaya Gönderme Akışı\n"
    "Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir."
)

def test_missing_role_reason_follows_lowest_score_chunk_only():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    company_admin_more_relevant = [
        make_chunk(COMPANY_ADMIN_REAL_TEXT, score=0.42),
        make_chunk(MUAYENE_ONAYLAMA_REAL_TEXT, score=0.60),
    ]
    result = find_missing_required_role(company_admin_more_relevant, ["Muayene Personeli"], roles, role_requirements)
    assert result == "Muayene|ISO 17020 Tanımlama"

    muayene_onaylama_more_relevant = [
        make_chunk(COMPANY_ADMIN_REAL_TEXT, score=0.60),
        make_chunk(MUAYENE_ONAYLAMA_REAL_TEXT, score=0.42),
    ]
    result_swapped = find_missing_required_role(muayene_onaylama_more_relevant, ["Muayene Personeli"], roles, role_requirements)
    assert result_swapped == "Muayene Onay Personeli"

EQUIPMENT_INVENTORY_REAL_TEXT = (
    "KURULUŞ TEST - Ekipman Envanteri\n"
    "Müşterilere ait, muayene edilen ekipmanların envanter olarak tutulduğu ekran."
)
EQUIPMENT_INSPECTION_REPORT_REAL_TEXT = (
    "Ekipman Muayene Raporu\n"
    "Ekipman muayene raporu, belirli bir yıl ve ekipman(lar) için yapılan muayenelerin grafiksel özetidir."
)

def test_equipmentinventory_index_not_blocked_by_coretrieved_inspection_report_chunk():
    from app.rag.role_guard import load_role_requirements

    roles = load_roles()
    role_requirements = load_role_requirements()
    chunks = [
        make_chunk(EQUIPMENT_INVENTORY_REAL_TEXT, score=0.4872),
        make_chunk(EQUIPMENT_INSPECTION_REPORT_REAL_TEXT, score=0.5609),
    ]

    result = find_missing_required_role(chunks, ["Muayene|ISO 17020 Tanımlama"], roles, role_requirements)
    assert result is None