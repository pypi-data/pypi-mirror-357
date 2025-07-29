import pandas as pd
from datetime import datetime, timedelta

class DatePlotter():

    def __init__(self, df, title):

        self.df = df.copy()
        
        self.title_dict = dict(
                    text=title.title(),
                    font=dict(color="#AE37FF"),
                    x=0
                )
        
        self.n = 35
        
        self.colors = [
            "#ae37ff", "#ab8bff", "#bbc6e2",
            "#8fb3e0", "#98c8d9", "#92e4c3",
            "#91de73", "#bdf07f", "#e5f993"
        ]

        self.axis_dict = dict(
                showline=True, 
                linewidth=2, 
                linecolor='rgba(0, 0, 0, 0.2)', 
                mirror=False, 
                title=None, 
                automargin=False,
                tickfont=dict(size=9)
            )
        self.legend_dict = dict(
                orientation="h",  # Horizontal legend
                yanchor="top",    # Align legend closer to the top of its container
                y=-0.15,           # Adjust position to reduce the gap
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            )
        
    def apply_filters(self, filters):
        df = self.df
        if filters:
            for col, values in filters.items():
                df = df[df[col].isin(values)]
        self.df = df

    def trim_to_date_range(self, days_back, date_col):
        self.df[date_col] = pd.to_datetime(self.df[date_col])
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()
        self.df = self.df[(self.df[date_col] >= start_date) & (self.df[date_col] <= end_date)]

    def convert_to_date_granularity(self, date_col ,granularity):
        if granularity == 'daily':
            self.df['period_start'] = self.df[date_col].dt.floor('D')
            self.df['period_end'] = self.df['period_start']
        elif granularity == 'weekly':
            self.df['period_start'] = self.df[date_col].dt.to_period('W').dt.start_time
            self.df['period_end'] = self.df[date_col].dt.to_period('W').dt.end_time
        elif granularity == 'monthly':
            self.df['period_start'] = self.df[date_col].dt.to_period('M').dt.start_time
            self.df['period_end'] = self.df[date_col].dt.to_period('M').dt.end_time
        else:
            raise ValueError("granularity must be one of 'daily', 'weekly', or 'monthly'.")

        # Combine the start and end into a single range string
        self.df['period'] = self.df['period_start'].dt.strftime('%Y-%m-%d') + '/' + self.df['period_end'].dt.strftime('%Y-%m-%d')

    def drop_incomplete_last_period_if_requested(self, date_col):
        
        self.df['period_end'] = pd.to_datetime(self.df['period_end']).dt.date
        self.df[date_col] = pd.to_datetime(self.df[date_col]).dt.date
        
        max_period = self.df['period_end'].max()
        max_date = self.df[date_col].max()
        if max_date < max_period:
            self.df= self.df[self.df['period_end'] != max_period]

    def compile_hover_tooltip(self, agg_df, date_col, granularity):
        """
        Generates a tooltip with a visually robust table using Unicode box-drawing
        characters. This creates a clear, aligned table without relying on specific
        fonts or HTML rendering.
        """
        # 1. Format the date/period part of the tooltip (unchanged)
        if granularity != 'daily':
            start = agg_df['period'].astype(str).str.split('/').str[0]
            end = agg_df['period'].astype(str).str.split('/').str[1]
            date_part = start + ' → ' + end
        else:
            date_part = agg_df['period'].astype(str).str.split('/').str[0]

        # 2. Prepare columns for the table
        value_cols = [c for c in agg_df.columns if c not in [date_col, 'hover_text', 'period', 'period_start']]

        if not value_cols:
            agg_df['hover_text'] = date_part
            return agg_df

        col_titles = {c: self.convert_str_2_title(c) for c in value_cols}

        # 3. Calculate inner column widths, adding space for padding
        inner_widths = {}
        for col_name in value_cols:
            title_width = len(col_titles[col_name])
            
            if agg_df[col_name].dtype in ['float64', 'int64']:
                # For numbers, format them first to get the true display width
                formatted_vals = agg_df[col_name].round(2).apply(lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}")
                max_val_width = formatted_vals.str.len().max()
            else:
                max_val_width = agg_df[col_name].astype(str).str.len().max()
            
            # The inner width of the cell is the max of title/value width + 2 for padding
            inner_widths[col_name] = max(title_width, max_val_width) + 2

        # 4. Create the static parts of the table structure
        widths = list(inner_widths.values())
        top_border    = "┌" + "┬".join(["─" * w for w in widths]) + "┐"
        header_line   = "│" + "│".join([col_titles[c].center(inner_widths[c]) for c in value_cols]) + "│"
        middle_border = "├" + "┼".join(["─" * w for w in widths]) + "┤"
        bottom_border = "└" + "┴".join(["─" * w for w in widths]) + "┘"

        # 5. Create the dynamic value rows for each data point
        padded_series_list = []
        for col_name in value_cols:
            width = inner_widths[col_name]
            
            # Format and pad each value in the column
            if agg_df[col_name].dtype in ['float64', 'int64']:
                formatted = agg_df[col_name].round(2).apply(lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}")
                # Right-justify numbers for better readability
                padded = formatted.str.rjust(width - 1) + " "
            else:
                formatted = agg_df[col_name].astype(str)
                # Left-justify text
                padded = " " + formatted.str.ljust(width - 1)
            
            padded_series_list.append(padded)

        # Combine the padded value columns into a single string series
        value_lines = "│" + padded_series_list[0].str.cat(padded_series_list[1:], sep="│") + "│"

        # 6. Assemble the final tooltip string using <br> for line breaks
        # We use <br> as it was in your original code and is more likely to be
        # interpreted correctly than a newline character.
        table_series = (
            top_border + "<br>" +
            header_line + "<br>" +
            middle_border + "<br>" +
            value_lines + "<br>" +
            bottom_border
        )

        agg_df['hover_text'] = date_part + "<br>" + table_series
        
        return agg_df

