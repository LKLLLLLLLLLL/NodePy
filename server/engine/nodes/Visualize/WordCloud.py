from ..BaseNode import BaseNode, register_node

@register_node
class WordCloudNode(BaseNode):
    """
    Node to generate a word cloud from table.
    Requires two user-specified columns as "word" and "frequency".
    """

    """
    Use wordcloud library to generate word cloud.
    Example use:
    wc = WordCloud(
        mask=mask,
        font_path="/System/Library/Fonts/STHeiti Medium.ttc",
        background_color="white",
        max_words=200,
        max_font_size=120,
        min_font_size=10,
        random_state=50,
        scale=10,
        repeat=False,
    )
    wc.generate_from_frequencies(keywords)
    plt.imshow(wc)
    plt.show()
    """
