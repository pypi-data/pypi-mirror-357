    import os
    from pathlib import Path

    def verifier_secrets():
        print("🔐 Vérification des secrets nécessaires...
")

        secrets = {
            "DISCORD_WEBHOOK_URL": "Lien du webhook Discord pour notifications automatiques"
        }

        missing = []
        for key in secrets:
            if os.getenv(key) is None:
                print(f"⚠️  {key} manquant – {secrets[key]}")
                missing.append(key)

        if missing:
            print("\n➡️ Ajoutez-les dans un fichier `.env` ou dans vos GitHub Secrets :")
            for key in missing:
                print(f"  - {key}")
            print("\n✅ Un fichier `.env.example` a été généré avec les clés nécessaires.")
            generer_env_example(secrets)

    def generer_env_example(secrets):
        content = "\n".join([f"{k}=" for k in secrets])
        Path(".env.example").write_text(content)

    if __name__ == "__main__":
        verifier_secrets()
