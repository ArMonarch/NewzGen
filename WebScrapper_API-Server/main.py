from NewsScrapper.BBC import BBC

def main() -> None:
    bbc = BBC()
    bbc.getArticles(5)
    return

if __name__ == "__main__":
    main()