from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum


class TypeDocument(str, Enum):
    DEVIS = "devis"
    FACTURE = "facture"


class StatutTraitement(str, Enum):
    ENVOYE = "envoyé"
    SUSPENDU = "suspendu"
    BROUILLON = "brouillon"


@dataclass
class FicheAchat:
    """Données extraites de la fiche de pré-remplissage normée."""

    # Champs obligatoires
    type_document: Optional[TypeDocument] = None
    reference_interne: Optional[str] = None
    date_reception: Optional[date] = None
    fournisseur_nom: Optional[str] = None
    objet_achat: Optional[str] = None
    montant_ht: Optional[Decimal] = None
    montant_tva: Optional[Decimal] = None
    montant_ttc: Optional[Decimal] = None
    devise: str = "EUR"
    codes_imputation: list[str] = field(default_factory=list)
    service_demandeur: Optional[str] = None
    destinataire_email: Optional[str] = None

    # Champs optionnels
    fournisseur_siret: Optional[str] = None
    numero_facture_devis: Optional[str] = None
    code_cpv_impose: Optional[str] = None
    observations: Optional[str] = None

    # GLB
    glb_requise: bool = False
    glb_categorie: Optional[str] = None
    glb_quantite: Optional[int] = None
    glb_numero_serie: Optional[str] = None
    glb_lieu_detention: Optional[str] = None
    glb_detenteur: Optional[str] = None

    # Pièces jointes déclarées
    pieces_jointes: list[str] = field(default_factory=list)


@dataclass
class AlerteAnomalie:
    code: str           # ex: "MONTANT_INCOHERENT", "CHAMP_MANQUANT"
    message: str
    champ: Optional[str] = None
    valeur_fiche: Optional[str] = None
    valeur_document: Optional[str] = None


@dataclass
class ResultatCPV:
    code: str
    libelle: str
    score: float


@dataclass
class DossierTraitement:
    """Représente un dossier complet en cours de traitement."""
    drive_file_id: str
    drive_file_name: str
    fiche: Optional[FicheAchat] = None
    alertes: list[AlerteAnomalie] = field(default_factory=list)
    cpv_proposes: list[ResultatCPV] = field(default_factory=list)
    cpv_retenu: Optional[ResultatCPV] = None
    chemin_bordereau: Optional[str] = None
    chemin_glb: Optional[str] = None
    statut: StatutTraitement = StatutTraitement.BROUILLON
    motif_suspension: Optional[str] = None

    @property
    def peut_envoyer_auto(self) -> bool:
        return len(self.alertes) == 0

    @property
    def nom_sortie(self) -> str:
        """Convention : YYYYMMDD_NP_RICM_NOM_ACHAT"""
        if self.fiche and self.fiche.date_reception and self.fiche.objet_achat:
            d = self.fiche.date_reception.strftime("%Y%m%d")
            nom = self.fiche.objet_achat.upper().replace(" ", "_")[:40]
            return f"{d}_NP_RICM_{nom}"
        return self.drive_file_name
