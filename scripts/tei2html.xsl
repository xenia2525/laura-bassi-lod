<?xml version="1.0" encoding="UTF-8"?>
<!--
  XML/TEI → HTML transformation for the Laura Bassi project.
  XSLT 1.0 (runs with lxml in tei2html.py, or with Saxon/xsltproc).

  Output: one HTML page with
    - the encoded text, where every annotated entity is highlighted by type
      and linked to its description;
    - an index of the entities described in the standOff, with links to
      Wikidata / VIAF / LC;
    - the events, the works and the bibliography.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei">

  <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-system="about:legacy-compat"/>

  <!-- every element with an xml:id can be found from a "#id" pointer -->
  <xsl:key name="entity" match="tei:*[@xml:id]" use="concat('#', @xml:id)"/>

  <!-- ================================================= page -->
  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title><xsl:value-of select="//tei:titleStmt/tei:title"/></title>
        <link rel="schema.DC" href="http://purl.org/dc/elements/1.1/"/>
        <meta name="DC.title" content="{//tei:titleStmt/tei:title}"/>
        <meta name="DC.creator" content="{//tei:titleStmt/tei:respStmt/tei:name}"/>
        <meta name="DC.source" content="{//tei:sourceDesc//tei:ptr/@target}"/>
        <meta name="DC.rights" content="CC BY-SA 4.0"/>
        <meta name="DC.language" content="en"/>
        <style>
          :root { --ink:#1d1d1f; --muted:#6b6b70; --line:#e4e2dc; --paper:#fbfaf7;
                  --person:#b4235a; --place:#2f7d4f; --org:#2d5bb8; --event:#a86a00;
                  --work:#6d3fb0; --concept:#4a5560; --quote:#8a3b12; }
          * { box-sizing:border-box; }
          body { margin:0; background:var(--paper); color:var(--ink);
                 font:17px/1.65 Georgia, "Times New Roman", serif; }
          header.page { padding:48px 20px 24px; border-bottom:1px solid var(--line); background:#fff; }
          header.page .inner, main { max-width:1180px; margin:0 auto; }
          header.page h1 { font-size:2.2rem; margin:0 0 6px; font-weight:normal; }
          header.page p { margin:2px 0; color:var(--muted); font:14px/1.5 system-ui, sans-serif; }
          main { display:grid; grid-template-columns:minmax(0,1fr) 340px; gap:40px; padding:32px 20px 80px; }
          article h2 { font-weight:normal; font-size:1.55rem; margin:2.2em 0 .4em; border-bottom:1px solid var(--line); padding-bottom:.2em; }
          article h3 { font-weight:normal; font-style:italic; font-size:1.2rem; margin:1.6em 0 .3em; }
          aside { font:14px/1.5 system-ui, sans-serif; }
          aside section { position:sticky; top:16px; }
          aside h2 { font-size:.8rem; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin:0 0 10px; }
          .legend span { display:inline-block; margin:0 10px 6px 0; }
          .e { text-decoration:none; color:inherit; border-bottom:2px solid; }
          .e:hover { background:#fff3c4; }
          .person{border-color:var(--person)} .place{border-color:var(--place)} .org{border-color:var(--org)}
          .event{border-color:var(--event); border-bottom-style:dotted} .work{border-color:var(--work)} .concept{border-color:var(--concept); border-bottom-style:dashed}
          .dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:baseline}
          q.quote { color:var(--quote); font-style:italic; quotes:none; }
          .foreign, .title-it { font-style:italic; }
          .socalled { font-variant:small-caps; }
          section.lists { grid-column:1 / -1; font:15px/1.5 system-ui, sans-serif; }
          section.lists h2 { font:normal 1.55rem Georgia, serif; border-bottom:1px solid var(--line); margin-top:2em; }
          .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:12px; }
          .card { background:#fff; border:1px solid var(--line); border-left:4px solid; padding:10px 12px; border-radius:4px; }
          .card:target { outline:3px solid #f3c64b; }
          .card b { display:block; }
          .card small { color:var(--muted); display:block; }
          .card a { color:var(--org); font-size:13px; margin-right:8px; }
          table { border-collapse:collapse; width:100%; background:#fff; }
          th, td { border:1px solid var(--line); padding:6px 10px; text-align:left; vertical-align:top; }
          th { background:#f2f0ea; font-weight:600; }
          ol.bibl li { margin-bottom:8px; }
          footer { text-align:center; color:var(--muted); font:13px system-ui, sans-serif; padding:30px 20px; border-top:1px solid var(--line); }
          @media (max-width:900px) { main { grid-template-columns:1fr; } aside section { position:static; } }
        </style>
      </head>
      <body>
        <header class="page">
          <div class="inner">
            <h1><xsl:value-of select="//tei:titleStmt/tei:title"/></h1>
            <p>Encoded by <xsl:value-of select="//tei:titleStmt/tei:respStmt/tei:name"/> · <xsl:value-of select="//tei:titleStmt/tei:funder"/></p>
            <p>Source: <a href="{//tei:sourceDesc//tei:ptr/@target}">English Wikipedia, "<xsl:value-of select="//tei:sourceDesc/tei:bibl/tei:title"/>", revision <xsl:value-of select="//tei:sourceDesc//tei:idno[@type='revision']"/> (<xsl:value-of select="//tei:sourceDesc//tei:date"/>)</a> · <xsl:value-of select="//tei:availability/tei:licence"/></p>
          </div>
        </header>
        <main>
          <article>
            <xsl:apply-templates select="//tei:text/tei:body"/>
          </article>
          <aside>
            <section>
              <h2>Legend</h2>
              <div class="legend">
                <span><i class="dot" style="background:var(--person)"></i>person</span>
                <span><i class="dot" style="background:var(--place)"></i>place</span>
                <span><i class="dot" style="background:var(--org)"></i>organisation</span>
                <span><i class="dot" style="background:var(--event)"></i>event</span>
                <span><i class="dot" style="background:var(--work)"></i>work</span>
                <span><i class="dot" style="background:var(--concept)"></i>concept</span>
              </div>
              <h2 style="margin-top:20px">Contents</h2>
              <ol>
                <xsl:for-each select="//tei:body/tei:div[tei:head]">
                  <li><a href="#{generate-id()}"><xsl:value-of select="tei:head"/></a></li>
                </xsl:for-each>
                <li><a href="#entities">Entities</a></li>
                <li><a href="#events">Events</a></li>
                <li><a href="#works">Works and bibliography</a></li>
              </ol>
              <h2 style="margin-top:20px">Numbers</h2>
              <p>
                <xsl:value-of select="count(//tei:body//*[@ref])"/> annotations ·
                <xsl:value-of select="count(//tei:standOff//tei:person | //tei:standOff//tei:place | //tei:standOff//tei:org)"/> people, places and organisations ·
                <xsl:value-of select="count(//tei:standOff//tei:event)"/> events ·
                <xsl:value-of select="count(//tei:standOff//tei:bibl)"/> works ·
                <xsl:value-of select="count(//tei:standOff//tei:relation)"/> relations
              </p>
            </section>
          </aside>

          <section class="lists" id="entities">
            <h2>Entities</h2>
            <div class="cards">
              <xsl:apply-templates select="//tei:standOff/tei:listPerson/tei:person"/>
              <xsl:apply-templates select="//tei:standOff/tei:listOrg/tei:org"/>
              <xsl:apply-templates select="//tei:standOff/tei:listPlace/tei:place"/>
              <xsl:apply-templates select="//tei:classDecl//tei:category"/>
            </div>

            <h2 id="events">Events</h2>
            <table>
              <tr><th>Date</th><th>Event</th><th>Participants</th><th>Carried out by</th><th>Place</th></tr>
              <xsl:for-each select="//tei:standOff/tei:listEvent/tei:event">
                <xsl:variable name="ptr" select="concat('#', @xml:id)"/>
                <tr id="{@xml:id}">
                  <td><xsl:value-of select="@when"/></td>
                  <td><xsl:value-of select="tei:label"/></td>
                  <td><xsl:call-template name="related"><xsl:with-param name="ptr" select="$ptr"/><xsl:with-param name="name" select="'hadParticipant'"/></xsl:call-template></td>
                  <td><xsl:call-template name="related"><xsl:with-param name="ptr" select="$ptr"/><xsl:with-param name="name" select="'carriedOutBy'"/></xsl:call-template></td>
                  <td><xsl:call-template name="related"><xsl:with-param name="ptr" select="$ptr"/><xsl:with-param name="name" select="'tookPlaceAt'"/></xsl:call-template></td>
                </tr>
              </xsl:for-each>
            </table>

            <h2 id="works">Works and bibliography</h2>
            <xsl:for-each select="//tei:standOff/tei:listBibl">
              <h3><xsl:value-of select="tei:head"/></h3>
              <ol class="bibl">
                <xsl:apply-templates select="tei:bibl"/>
              </ol>
            </xsl:for-each>
          </section>
        </main>
        <footer>
          Generated from <code>data/laura_bassi.xml</code> with <code>scripts/tei2html.xsl</code>.
        </footer>
      </body>
    </html>
  </xsl:template>

  <!-- ================================================= text -->
  <xsl:template match="tei:body/tei:div">
    <section id="{generate-id()}"><xsl:apply-templates/></section>
  </xsl:template>
  <xsl:template match="tei:div/tei:div">
    <section><xsl:apply-templates/></section>
  </xsl:template>
  <xsl:template match="tei:body/tei:div/tei:head">
    <h2><xsl:apply-templates/></h2>
  </xsl:template>
  <xsl:template match="tei:div/tei:div/tei:head">
    <h3><xsl:apply-templates/></h3>
  </xsl:template>
  <xsl:template match="tei:p"><p><xsl:apply-templates/></p></xsl:template>
  <xsl:template match="tei:list"><ul><xsl:apply-templates select="tei:item"/></ul></xsl:template>
  <xsl:template match="tei:item"><li><xsl:apply-templates/></li></xsl:template>

  <!-- annotated entities: a link to the card / row describing them -->
  <xsl:template match="tei:body//*[@ref and starts-with(@ref,'#')]">
    <xsl:variable name="target" select="key('entity', @ref)"/>
    <xsl:variable name="class">
      <xsl:choose>
        <xsl:when test="local-name($target)='person'">person</xsl:when>
        <xsl:when test="local-name($target)='place'">place</xsl:when>
        <xsl:when test="local-name($target)='org'">org</xsl:when>
        <xsl:when test="local-name($target)='event'">event</xsl:when>
        <xsl:when test="local-name($target)='bibl'">work</xsl:when>
        <xsl:otherwise>concept</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <!-- nested annotations (e.g. a title inside an event) become <span>, since links cannot nest -->
    <xsl:variable name="tag">
      <xsl:choose>
        <xsl:when test="ancestor::*[@ref and ancestor::tei:body]">span</xsl:when>
        <xsl:otherwise>a</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:element name="{$tag}">
      <xsl:attribute name="class">e <xsl:value-of select="$class"/></xsl:attribute>
      <xsl:if test="$tag='a'"><xsl:attribute name="href"><xsl:value-of select="@ref"/></xsl:attribute></xsl:if>
      <xsl:attribute name="title">
        <xsl:value-of select="$class"/>
        <xsl:text>: </xsl:text>
        <xsl:value-of select="normalize-space(($target/tei:persName | $target/tei:placeName | $target/tei:orgName | $target/tei:label | $target/tei:title | $target/tei:catDesc)[1])"/>
      </xsl:attribute>
      <xsl:if test="@when"><xsl:attribute name="data-when"><xsl:value-of select="@when"/></xsl:attribute></xsl:if>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="tei:date"><time datetime="{@when}"><xsl:apply-templates/></time></xsl:template>
  <xsl:template match="tei:date[@from]"><time datetime="{@from}"><xsl:apply-templates/></time></xsl:template>
  <xsl:template match="tei:q"><q class="quote" id="{@xml:id}" cite="{@who}"><xsl:apply-templates/></q></xsl:template>
  <xsl:template match="tei:foreign"><i class="foreign" lang="{@xml:lang}"><xsl:apply-templates/></i></xsl:template>
  <xsl:template match="tei:title[not(@ref)]"><cite><xsl:apply-templates/></cite></xsl:template>
  <xsl:template match="tei:soCalled"><span class="socalled"><xsl:apply-templates/></span></xsl:template>

  <!-- ================================================= entity cards -->
  <xsl:template name="links">
    <xsl:if test="@sameAs"><a href="{@sameAs}">Wikidata</a></xsl:if>
    <xsl:for-each select="tei:idno[@type='VIAF']"><a href="{.}">VIAF</a></xsl:for-each>
    <xsl:for-each select="tei:idno[@type='LC']"><a href="{.}">LC</a></xsl:for-each>
    <xsl:if test="@corresp"><a href="{@corresp}">LCSH</a></xsl:if>
  </xsl:template>

  <xsl:template match="tei:person">
    <div class="card" id="{@xml:id}" style="border-left-color:var(--person)">
      <b><xsl:value-of select="tei:persName[1]"/></b>
      <xsl:if test="tei:persName[2]"><small>also: <xsl:value-of select="tei:persName[2]"/></small></xsl:if>
      <small>
        <xsl:value-of select="tei:occupation[1]"/>
        <xsl:if test="tei:birth/@when"> · <xsl:value-of select="tei:birth/@when"/> – <xsl:value-of select="tei:death/@when"/></xsl:if>
      </small>
      <xsl:call-template name="links"/>
    </div>
  </xsl:template>

  <xsl:template match="tei:org">
    <div class="card" id="{@xml:id}" style="border-left-color:var(--org)">
      <b><xsl:value-of select="tei:orgName[1]"/></b>
      <small>organisation<xsl:if test="tei:note"> · <xsl:value-of select="tei:note"/></xsl:if></small>
      <xsl:call-template name="links"/>
    </div>
  </xsl:template>

  <xsl:template match="tei:place">
    <div class="card" id="{@xml:id}" style="border-left-color:var(--place)">
      <b><xsl:value-of select="tei:placeName[1]"/></b>
      <small>place<xsl:if test="tei:note"> · <xsl:value-of select="tei:note"/></xsl:if></small>
      <xsl:call-template name="links"/>
    </div>
  </xsl:template>

  <xsl:template match="tei:category">
    <div class="card" id="{@xml:id}" style="border-left-color:var(--concept)">
      <b><xsl:value-of select="tei:catDesc"/></b>
      <small>concept</small>
      <xsl:call-template name="links"/>
    </div>
  </xsl:template>

  <xsl:template match="tei:standOff//tei:bibl">
    <li id="{@xml:id}">
      <xsl:value-of select="tei:author"/>
      <xsl:if test="tei:author">, </xsl:if>
      <i><xsl:value-of select="tei:title[1]"/></i>
      <xsl:if test="tei:title[@level='j']">, <xsl:value-of select="tei:title[@level='j']"/></xsl:if>
      <xsl:if test="tei:biblScope[@unit='volume']"> <xsl:value-of select="concat(' ', tei:biblScope[@unit='volume'])"/></xsl:if>
      <xsl:if test="tei:publisher">, <xsl:value-of select="tei:publisher"/></xsl:if>
      <xsl:text> (</xsl:text><xsl:value-of select="tei:date"/><xsl:text>)</xsl:text>
      <xsl:if test="tei:biblScope[@unit='page']">, pp. <xsl:value-of select="tei:biblScope[@unit='page']"/></xsl:if>
      <xsl:for-each select="tei:idno[@type='DOI']"> · <a href="https://doi.org/{.}">doi:<xsl:value-of select="."/></a></xsl:for-each>
      <xsl:if test="@sameAs"> · <a href="{@sameAs}">Wikidata</a></xsl:if>
      <xsl:if test="tei:note"> — <small><xsl:value-of select="tei:note"/></small></xsl:if>
    </li>
  </xsl:template>

  <!-- names of the entities related to an event through a given relation -->
  <xsl:template name="related">
    <xsl:param name="ptr"/>
    <xsl:param name="name"/>
    <xsl:for-each select="//tei:relation[@name=$name][contains(concat(' ', @active, ' '), concat(' ', $ptr, ' '))]">
      <xsl:call-template name="names">
        <xsl:with-param name="list" select="normalize-space(@passive)"/>
      </xsl:call-template>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="names">
    <xsl:param name="list"/>
    <xsl:variable name="first">
      <xsl:choose>
        <xsl:when test="contains($list, ' ')"><xsl:value-of select="substring-before($list, ' ')"/></xsl:when>
        <xsl:otherwise><xsl:value-of select="$list"/></xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="t" select="key('entity', $first)"/>
    <a href="{$first}"><xsl:value-of select="($t/tei:persName | $t/tei:placeName | $t/tei:orgName)[1]"/></a>
    <xsl:if test="contains($list, ' ')">
      <xsl:text>, </xsl:text>
      <xsl:call-template name="names"><xsl:with-param name="list" select="substring-after($list, ' ')"/></xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- the header and standOff are not copied as text -->
  <xsl:template match="tei:teiHeader | tei:standOff"/>
</xsl:stylesheet>
