from streamlit.components.v1 import html


class Current:
    def navigateTo(self, target: str, query: str = None):
        # JS-safe fallback
        query_js = f"'{query}'" if query else "undefined"

        html(
            f"""
            <script>
                window.parent.navigateCurrentMiniApp('{target}', {query_js});
            </script>
            """,
            height=0,
        )
