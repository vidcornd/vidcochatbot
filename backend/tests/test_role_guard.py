import pytest
from app.rag.role_guard import find_missing_required_role, load_roles

REQUIREMENTS = {
    "muayene_onaylama": {
        "required_roles": ["Muayene Onay Personeli"],
        "trigger_terms": ["kendi muayenesini kendisi onaylayabilir"],
    }
}

def make_chunk(content: str) -> dict:
    return {"content": content}

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

def test_stops_at_first_chunk_matching_a_requirement():
    roles = load_roles()
    chunks = [
        make_chunk("Genel bilgi, tetikleyici terim yok."),
        make_chunk("Muayeneyi yapan kişi onay yetkisine de sahipse kendi muayenesini kendisi onaylayabilir."),
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