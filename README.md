# tractatusSky

These Python scripts processes a JSON-encoded version of Ludwig Wittgenstein's *Tractatus Logico-Philosophicus* and posts its propositions to [Bluesky](https://bsky.app), retaining the nested structure of the text. It also supports posting propositions with their associated images. See `@tractatussky.bsky.social`.

## Features

- **Preprocessing**: Cleans and formats the text from the raw JSON input file `tractatus.json` using `BeautifulSoup` `bs4`, etc.
- **Image Handling**: Handles images associated with propositions, preparing them for posting alongside their respective text.
- **Hierarchical Posting**: Posts each proposition to Bluesky maintaining the nested tree structure and relationships between propositions.
- **Character Limit Management**: Propositions that exceed the 300-character limit imposed by Bluesky are chunked in parts 1/n, 2/n, etc.

## Requirements

- Python 3.8+
- Libraries:
  - `beautifulsoup4`
  - `atproto`
  - `bs4`
- A JSON file containing the raw *Tractatus* in a nested structure (e.g., `tractatus.json`).
- The images in the `images` directory, named as `{num}.png` where `{num}` corresponds to the proposition number.
- Bluesky credentials.

## Usage

1. Run the script to preprocess the data:

   ```bash
   python preprocess.py
   ```

   This will:
   - Remove the preface from the JSON structure.
   - Clean and format the text.
   - Generate two new files:
     - `processed_tractatus.json`: Preprocessed *Tractatus* data.
     - `images.json`: Image metadata for propositions containing images.

The JSON structure should look like this:

```json
[
  {
    "num": "1",
    "text": "The world is all that is the case.",
    "children": [
      {
        "num": "1.1",
        "text": "The world is the totality of facts, not of things.",
        "children": [
          {
            "num": "1.1.1",
            "text": "The world is determined by the facts, and by their being _all_ the facts.",
            "children": []
          }
        ]
      }
    ]
  }
  // more propositions
]
```

The `images.json` file should look like this:

```json
{
  "4.2.7": ["base64encoded image data"],
  "4.3.1": ["base64encoded image data"]
  // more images
}
```

2. Run the script to post the propositions to Bluesky:

   ```bash
   python post.py
   ```

   The script will recursively post propositions to Bluesky, ensuring the nested structure is maintained. If images are present, they will be posted alongside the relevant propositions.

## Example Output

- A root proposition will be posted as a standalone message.
- Subpropositions will appear as replies, preserving the logical structure.
- Example of hierarchical posting:

```plaintext
1 The world is all that is the case.
   ↳ 1.1 The world is the totality of facts, not of things.
       ↳ 1.1.1 Facts are states of affairs.
```

## Comments

- Bluesky is currectly limited in terms of its rich text support. As a result, the text formatting may not alway be perfect. For example, for italics I've used underscores, subsscripts and superscripts are not supported. In cases where it was impossible to typsest a formula in a way that made sense in plain text, I've added an image to the post.
- The character limit of 300 characters per post may result in some propositions being split into multiple parts. This is handled by the script, but it slightly distorts the tree structure. The parts will be siblings marked with (1/n), (2/n), etc., and if the proposition has children, they will be posted as replies to the last part.
- The script does not handle the preface of the *Tractatus*, or footnotes.
- Unfortunatly, Bluesky displays threads in a way that the tree structure is not immediately apparent. It shows the leftmost branch first, then the next leftmost branch, etc. After posting the structure will be there in the Bluesky database, but it is not displayed in the the most intuitive way. Other clients could display the tree structure in a more intuitive way.

## Acknowledgments

- The *Tractatus Logico-Philosophicus* by Ludwig Wittgenstein serves as the core text for this project. It in the public domain. The English translation used is the Pears/McGuinness.
- The raw JSON-encoded version is based on Kevin Klement's [Tractatus project](https://bitbucket.org/frabjous/tractatus/src/master/) and Nico Chilla's [Tractatus Tree](https://github.com/nchilla/tractatus-tree) project

--
[rabern 2025](brianrabern.net)

"Wovon man nicht sprechen kann, darüber muss man schweigen"
