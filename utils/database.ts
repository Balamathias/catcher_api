export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instanciate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.0 (ec89f6b)"
  }
  public: {
    Tables: {
      account: {
        Row: {
          account_name: string | null
          account_number: string | null
          bank_code: string | null
          bank_name: string | null
          bvn: string | null
          created_at: string
          id: number
          metadata: Json | null
          nin: string | null
          palmpay_account_name: string | null
          palmpay_account_number: string | null
          reference: string | null
          status: string | null
          updated_at: string | null
          user: string
        }
        Insert: {
          account_name?: string | null
          account_number?: string | null
          bank_code?: string | null
          bank_name?: string | null
          bvn?: string | null
          created_at?: string
          id?: number
          metadata?: Json | null
          nin?: string | null
          palmpay_account_name?: string | null
          palmpay_account_number?: string | null
          reference?: string | null
          status?: string | null
          updated_at?: string | null
          user: string
        }
        Update: {
          account_name?: string | null
          account_number?: string | null
          bank_code?: string | null
          bank_name?: string | null
          bvn?: string | null
          created_at?: string
          id?: number
          metadata?: Json | null
          nin?: string | null
          palmpay_account_name?: string | null
          palmpay_account_number?: string | null
          reference?: string | null
          status?: string | null
          updated_at?: string | null
          user?: string
        }
        Relationships: [
          {
            foreignKeyName: "account_user_fkey"
            columns: ["user"]
            isOneToOne: true
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      announcements: {
        Row: {
          assets: Json | null
          created_at: string
          description: string | null
          id: number
          published: boolean | null
          title: string
          type: string | null
        }
        Insert: {
          assets?: Json | null
          created_at?: string
          description?: string | null
          id?: number
          published?: boolean | null
          title: string
          type?: string | null
        }
        Update: {
          assets?: Json | null
          created_at?: string
          description?: string | null
          id?: number
          published?: boolean | null
          title?: string
          type?: string | null
        }
        Relationships: []
      }
      app_config: {
        Row: {
          created_at: string
          id: number
          name: string | null
          value: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          name?: string | null
          value?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          name?: string | null
          value?: string | null
        }
        Relationships: []
      }
      beneficiaries: {
        Row: {
          created_at: string
          frequency: number | null
          id: string
          last_used: string | null
          network: string | null
          phone: string | null
          user: string | null
        }
        Insert: {
          created_at?: string
          frequency?: number | null
          id?: string
          last_used?: string | null
          network?: string | null
          phone?: string | null
          user?: string | null
        }
        Update: {
          created_at?: string
          frequency?: number | null
          id?: string
          last_used?: string | null
          network?: string | null
          phone?: string | null
          user?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "beneficiaries_user_fkey"
            columns: ["user"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      chat_room: {
        Row: {
          created_at: string
          id: string
          participants: string[] | null
          user_id: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          participants?: string[] | null
          user_id?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          participants?: string[] | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "chat_room_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      chats: {
        Row: {
          attachment_url: string | null
          avatar: string | null
          chat_room: string | null
          created_at: string
          id: number
          message: string
          role: string | null
          user_id: string | null
        }
        Insert: {
          attachment_url?: string | null
          avatar?: string | null
          chat_room?: string | null
          created_at?: string
          id?: number
          message: string
          role?: string | null
          user_id?: string | null
        }
        Update: {
          attachment_url?: string | null
          avatar?: string | null
          chat_room?: string | null
          created_at?: string
          id?: number
          message?: string
          role?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "chats_chat_room_fkey"
            columns: ["chat_room"]
            isOneToOne: false
            referencedRelation: "chat_room"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "chats_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      education: {
        Row: {
          cashback: number | null
          created_at: string
          id: number
          name: string | null
          price: number | null
          service_type: string | null
          variation_code: string | null
        }
        Insert: {
          cashback?: number | null
          created_at?: string
          id?: number
          name?: string | null
          price?: number | null
          service_type?: string | null
          variation_code?: string | null
        }
        Update: {
          cashback?: number | null
          created_at?: string
          id?: number
          name?: string | null
          price?: number | null
          service_type?: string | null
          variation_code?: string | null
        }
        Relationships: []
      }
      electricity: {
        Row: {
          alias: string | null
          created_at: string
          id: number
          metadata: Json | null
          name: string | null
          service_id: string | null
          thumbnail: string | null
        }
        Insert: {
          alias?: string | null
          created_at?: string
          id?: number
          metadata?: Json | null
          name?: string | null
          service_id?: string | null
          thumbnail?: string | null
        }
        Update: {
          alias?: string | null
          created_at?: string
          id?: number
          metadata?: Json | null
          name?: string | null
          service_id?: string | null
          thumbnail?: string | null
        }
        Relationships: []
      }
      epins: {
        Row: {
          created_at: string
          data: Json | null
          id: number
          network: string | null
          used: boolean | null
          user: string | null
        }
        Insert: {
          created_at?: string
          data?: Json | null
          id?: number
          network?: string | null
          used?: boolean | null
          user?: string | null
        }
        Update: {
          created_at?: string
          data?: Json | null
          id?: number
          network?: string | null
          used?: boolean | null
          user?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "epins_user_fkey"
            columns: ["user"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      gsub: {
        Row: {
          commission: number | null
          created_at: string
          duration: string | null
          id: number
          is_active: boolean | null
          is_hidden: boolean | null
          name: string | null
          network: string | null
          price: number | null
          quantity: string | null
          service_id: string | null
          value: string | null
        }
        Insert: {
          commission?: number | null
          created_at?: string
          duration?: string | null
          id?: number
          is_active?: boolean | null
          is_hidden?: boolean | null
          name?: string | null
          network?: string | null
          price?: number | null
          quantity?: string | null
          service_id?: string | null
          value?: string | null
        }
        Update: {
          commission?: number | null
          created_at?: string
          duration?: string | null
          id?: number
          is_active?: boolean | null
          is_hidden?: boolean | null
          name?: string | null
          network?: string | null
          price?: number | null
          quantity?: string | null
          service_id?: string | null
          value?: string | null
        }
        Relationships: []
      }
      history: {
        Row: {
          amount: number | null
          balance_after: number | null
          balance_before: number | null
          commission: number | null
          created_at: string
          description: string | null
          email: string | null
          id: number
          meta_data: Json | null
          provider: string | null
          request_id: string | null
          source: string | null
          status: string | null
          title: string | null
          transaction_id: string | null
          type: string | null
          updated_at: string | null
          user: string | null
          search_transactions: string | null
        }
        Insert: {
          amount?: number | null
          balance_after?: number | null
          balance_before?: number | null
          commission?: number | null
          created_at?: string
          description?: string | null
          email?: string | null
          id?: number
          meta_data?: Json | null
          provider?: string | null
          request_id?: string | null
          source?: string | null
          status?: string | null
          title?: string | null
          transaction_id?: string | null
          type?: string | null
          updated_at?: string | null
          user?: string | null
        }
        Update: {
          amount?: number | null
          balance_after?: number | null
          balance_before?: number | null
          commission?: number | null
          created_at?: string
          description?: string | null
          email?: string | null
          id?: number
          meta_data?: Json | null
          provider?: string | null
          request_id?: string | null
          source?: string | null
          status?: string | null
          title?: string | null
          transaction_id?: string | null
          type?: string | null
          updated_at?: string | null
          user?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "history_user_fkey"
            columns: ["user"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      n3t: {
        Row: {
          cash_back: number
          commission: number
          duration: string
          id: number
          is_active: boolean
          is_hidden: boolean | null
          name: string
          network: string | null
          price: number
          profit: number
          quantity: string
          service_id: string
          value: number
        }
        Insert: {
          cash_back: number
          commission: number
          duration: string
          id?: number
          is_active: boolean
          is_hidden?: boolean | null
          name: string
          network?: string | null
          price: number
          profit: number
          quantity: string
          service_id: string
          value: number
        }
        Update: {
          cash_back?: number
          commission?: number
          duration?: string
          id?: number
          is_active?: boolean
          is_hidden?: boolean | null
          name?: string
          network?: string | null
          price?: number
          profit?: number
          quantity?: string
          service_id?: string
          value?: number
        }
        Relationships: []
      }
      otp_requests: {
        Row: {
          expires_at: string
          id: number
          otp: string
          used: boolean | null
          user_id: string | null
        }
        Insert: {
          expires_at: string
          id?: number
          otp: string
          used?: boolean | null
          user_id?: string | null
        }
        Update: {
          expires_at?: string
          id?: number
          otp?: string
          used?: boolean | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "otp_requests_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      profile: {
        Row: {
          avatar: string | null
          created_at: string
          email: string | null
          full_name: string | null
          id: string
          onboarded: boolean | null
          phone: string | null
          phone_numbers: string[] | null
          pin: string | null
          role: string | null
          security_answer: string | null
          security_question: string | null
          state: string | null
          unique_code: string | null
          updated_at: string | null
          username: string | null
        }
        Insert: {
          avatar?: string | null
          created_at?: string
          email?: string | null
          full_name?: string | null
          id: string
          onboarded?: boolean | null
          phone?: string | null
          phone_numbers?: string[] | null
          pin?: string | null
          role?: string | null
          security_answer?: string | null
          security_question?: string | null
          state?: string | null
          unique_code?: string | null
          updated_at?: string | null
          username?: string | null
        }
        Update: {
          avatar?: string | null
          created_at?: string
          email?: string | null
          full_name?: string | null
          id?: string
          onboarded?: boolean | null
          phone?: string | null
          phone_numbers?: string[] | null
          pin?: string | null
          role?: string | null
          security_answer?: string | null
          security_question?: string | null
          state?: string | null
          unique_code?: string | null
          updated_at?: string | null
          username?: string | null
        }
        Relationships: []
      }
      ratings: {
        Row: {
          comment: string | null
          created_at: string
          id: string
          rating: number | null
          status: string | null
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          comment?: string | null
          created_at?: string
          id?: string
          rating?: number | null
          status?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          comment?: string | null
          created_at?: string
          id?: string
          rating?: number | null
          status?: string | null
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "ratings_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      referrals: {
        Row: {
          created_at: string
          device: string | null
          email: string | null
          id: string
          ip: string | null
          referred: string | null
          referrer: string | null
          reward: number | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string
          device?: string | null
          email?: string | null
          id?: string
          ip?: string | null
          referred?: string | null
          referrer?: string | null
          reward?: number | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string
          device?: string | null
          email?: string | null
          id?: string
          ip?: string | null
          referred?: string | null
          referrer?: string | null
          reward?: number | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "referrals_referred_fkey"
            columns: ["referred"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "referrals_referrer_fkey"
            columns: ["referrer"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["unique_code"]
          },
        ]
      }
      security_profile: {
        Row: {
          created_at: string
          details: string | null
          id: number
          severity: string | null
          type: string | null
          user: string | null
        }
        Insert: {
          created_at?: string
          details?: string | null
          id?: number
          severity?: string | null
          type?: string | null
          user?: string | null
        }
        Update: {
          created_at?: string
          details?: string | null
          id?: number
          severity?: string | null
          type?: string | null
          user?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "security_profile_user_fkey"
            columns: ["user"]
            isOneToOne: false
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
      tv: {
        Row: {
          amount: number | null
          cashback: number | null
          created_at: string
          fixed_price: boolean | null
          id: number
          name: string | null
          provider: string | null
          variation_code: string | null
        }
        Insert: {
          amount?: number | null
          cashback?: number | null
          created_at?: string
          fixed_price?: boolean | null
          id?: number
          name?: string | null
          provider?: string | null
          variation_code?: string | null
        }
        Update: {
          amount?: number | null
          cashback?: number | null
          created_at?: string
          fixed_price?: boolean | null
          id?: number
          name?: string | null
          provider?: string | null
          variation_code?: string | null
        }
        Relationships: []
      }
      vtpass: {
        Row: {
          commission: number | null
          created_at: string
          duration: string | null
          id: number
          is_active: boolean | null
          is_hidden: boolean | null
          name: string | null
          network: string | null
          price: number | null
          quantity: string | null
          service_id: string | null
          value: string | null
        }
        Insert: {
          commission?: number | null
          created_at?: string
          duration?: string | null
          id?: number
          is_active?: boolean | null
          is_hidden?: boolean | null
          name?: string | null
          network?: string | null
          price?: number | null
          quantity?: string | null
          service_id?: string | null
          value?: string | null
        }
        Update: {
          commission?: number | null
          created_at?: string
          duration?: string | null
          id?: number
          is_active?: boolean | null
          is_hidden?: boolean | null
          name?: string | null
          network?: string | null
          price?: number | null
          quantity?: string | null
          service_id?: string | null
          value?: string | null
        }
        Relationships: []
      }
      wallet: {
        Row: {
          balance: number | null
          bonus_claimed: boolean | null
          cashback_balance: number | null
          created_at: string
          email: string | null
          id: number
          meta_data: Json | null
          updated_at: string | null
          user: string
        }
        Insert: {
          balance?: number | null
          bonus_claimed?: boolean | null
          cashback_balance?: number | null
          created_at?: string
          email?: string | null
          id?: number
          meta_data?: Json | null
          updated_at?: string | null
          user: string
        }
        Update: {
          balance?: number | null
          bonus_claimed?: boolean | null
          cashback_balance?: number | null
          created_at?: string
          email?: string | null
          id?: number
          meta_data?: Json | null
          updated_at?: string | null
          user?: string
        }
        Relationships: [
          {
            foreignKeyName: "wallet_user_fkey"
            columns: ["user"]
            isOneToOne: true
            referencedRelation: "profile"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      charge_cashback_balance: {
        Args: { user_id: string; amount: number }
        Returns: undefined
      }
      charge_wallet: {
        Args: {
          user_id: string
          amount: number
          cashback?: number
          charge_from?: string
        }
        Returns: undefined
      }
      charge_wallet_balance: {
        Args: { user_id: string; amount: number }
        Returns: undefined
      }
      get_total_cashback_amount: {
        Args: { start_date?: string; end_date?: string }
        Returns: number
      }
      get_total_deposits: {
        Args: Record<PropertyKey, never>
        Returns: number
      }
      get_total_transactions_amount: {
        Args: { start_date?: string; end_date?: string }
        Returns: number
      }
      get_total_wallet_balance: {
        Args: { start_date?: string; end_date?: string }
        Returns: number
      }
      get_wallet_fund_totals: {
        Args: { start_date?: string; end_date?: string }
        Returns: {
          total_settlement_amount: number
          total_amount_paid: number
          net_amount: number
        }[]
      }
      modify_wallet_balance: {
        Args: { user_id: string; amount: number; new_cashback_balance: number }
        Returns: undefined
      }
      search_history: {
        Args: {
          search_query: string
          search_fields: string[]
          page: number
          per_page: number
        }
        Returns: {
          id: string
          title: string
          description: string
          transaction_id: string
          email: string
          avatar: string
          full_name: string
        }[]
      }
      search_transactions: {
        Args: { "": Database["public"]["Tables"]["history"]["Row"] }
        Returns: string
      }
      transfer_money: {
        Args: {
          sender_wallet_id: string
          recipient_wallet_id: string
          amount: number
        }
        Returns: undefined
      }
      update_cashback_balance: {
        Args: { user_id: string; cashback: number }
        Returns: undefined
      }
      update_wallet_balance: {
        Args: { user_id: string; amount: number; charge_from?: string }
        Returns: undefined
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
